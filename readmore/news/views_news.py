from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import NewsArticle, ReadHistory

@login_required
def news_list(request):
    articles = NewsArticle.objects.order_by('-published_at')[:30]
    read_ids = set(ReadHistory.objects.filter(user=request.user).values_list('article_id', flat=True))
    return render(request, 'news_list.html', {
        'articles': articles,
        'read_ids': read_ids,
    })

@login_required
def mark_read(request, article_id):
    article = get_object_or_404(NewsArticle, id=article_id)
    if not ReadHistory.objects.filter(user=request.user, article=article).exists():
        ReadHistory.objects.create(user=request.user, article=article)
    return redirect('news_list')

@login_required
def article_detail(request, article_id):
    article = get_object_or_404(NewsArticle, id=article_id)
    # Mark as read if not already
    ReadHistory.objects.get_or_create(user=request.user, article=article)
    return render(request, 'article_detail.html', {'article': article})

import feedparser
from celery import shared_task
from .models import NewsArticle
from django.utils import timezone

RSS_FEEDS = [
    'https://rss.cnn.com/rss/edition.rss',
    'https://feeds.bbci.co.uk/news/rss.xml',
    # Add more feeds as needed
]

@shared_task
def fetch_news():
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            url = entry.get('link')
            if not NewsArticle.objects.filter(url=url).exists():
                NewsArticle.objects.create(
                    title=entry.get('title', '')[:512],
                    url=url,
                    source=feed_url,
                    published_at=timezone.now(),  # You can parse entry.published if available
                    summary=entry.get('summary', '')
                )

from .models import UserProfile, Transaction

@shared_task
def convert_all_points_to_coins():
    CONVERSION_RATE = 1000
    for user_profile in UserProfile.objects.all():
        coins_to_credit = user_profile.balance // CONVERSION_RATE
        if coins_to_credit > 0:
            user_profile.balance -= coins_to_credit * CONVERSION_RATE
            user_profile.coin_balance += coins_to_credit
            user_profile.save()
            Transaction.objects.create(
                user=user_profile.user,
                type='convert',
                amount=coins_to_credit,
                points=-coins_to_credit * CONVERSION_RATE,
                coins=coins_to_credit,
                description=f'Auto-converted {coins_to_credit * CONVERSION_RATE} points to {coins_to_credit} coins at midnight.'
            )

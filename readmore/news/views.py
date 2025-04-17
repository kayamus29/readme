from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import UserProfile, ReadHistory, TaskCompletion, DailyTask, ManualTask
import datetime


from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .forms import EmailOrUsernameAuthenticationForm

class CustomLoginView(LoginView):
    authentication_form = EmailOrUsernameAuthenticationForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hide_nav'] = True
        return context

@login_required
def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Ensure UserProfile is created
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def dashboard(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    articles_read = ReadHistory.objects.filter(user=request.user).count()
    tasks_completed = TaskCompletion.objects.filter(user=request.user).count()
    # For dashboard news preview
    from .models import NewsArticle
    latest_article = NewsArticle.objects.order_by('-published_at').first()
    context = {
        'user_profile': user_profile,
        'articles_read': articles_read,
        'tasks_completed': tasks_completed,
        'latest_article': latest_article,
        'is_premium': user_profile.is_premium,
    }
    return render(request, 'dashboard.html', context)

@login_required
def daily_task_view(request):
    today = datetime.date.today()
    daily_task = DailyTask.objects.filter(date=today).first()
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    completed = False
    correct = False
    if request.method == 'POST' and daily_task:
        answer = request.POST.get('answer', '').strip()
        if answer.lower() == daily_task.correct_answer.lower():
            correct = True
            # Award points with multiplier, but cap for non-premium
            from .models import Transaction
            today_earned = Transaction.objects.filter(user=request.user, type='earn', created_at__date=today).aggregate(models.Sum('points'))['points__sum'] or 0
            points = 50 * user_profile.get_earning_multiplier()
            if not user_profile.is_premium and today_earned >= 1000:
                # Show popup only once per 24 hours
                last_popup = request.session.get('last_daily_cap_popup')
                now = timezone.now()
                show_daily_cap_popup = False
                if not last_popup or (now - timezone.datetime.fromisoformat(last_popup)).days >= 1:
                    show_daily_cap_popup = True
                    request.session['last_daily_cap_popup'] = now.isoformat()
                context['show_daily_cap_popup'] = show_daily_cap_popup
                pass  # Non-premium: cap reached, do not award more
            elif not user_profile.is_premium and today_earned + points > 1000:
                points = max(0, 1000 - today_earned)  # Only allow up to cap
                user_profile.balance += points
                user_profile.save()
                TaskCompletion.objects.create(user=request.user, manual_task=None)
            else:
                user_profile.balance += points
                user_profile.save()
                TaskCompletion.objects.create(user=request.user, manual_task=None)
            completed = True
    elif daily_task and TaskCompletion.objects.filter(user=request.user, manual_task__isnull=True, completed_at__date=today).exists():
        completed = True
    return render(request, 'daily_task.html', {'daily_task': daily_task, 'completed': completed, 'correct': correct})

def terms_view(request):
    from django.shortcuts import render
    return render(request, 'terms.html')

def custom_logout_view(request):
    from django.contrib.auth import logout
    from django.shortcuts import redirect
    logout(request)
    return redirect('/login/')

@login_required
def profile_view(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'user_profile': user_profile})

@login_required
def manual_tasks_view(request):
    tasks = ManualTask.objects.filter(is_active=True)
    completed_ids = set(TaskCompletion.objects.filter(user=request.user).values_list('manual_task_id', flat=True))
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        task = get_object_or_404(ManualTask, id=task_id)
        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if task.id not in completed_ids:
            from .models import Transaction
            today = datetime.date.today()
            today_earned = Transaction.objects.filter(user=request.user, type='earn', created_at__date=today).aggregate(models.Sum('points'))['points__sum'] or 0
            points = task.points * user_profile.get_earning_multiplier()
            if not user_profile.is_premium and today_earned >= 1000:
                # Show popup only once per 24 hours
                last_popup = request.session.get('last_daily_cap_popup')
                now = timezone.now()
                show_daily_cap_popup = False
                if not last_popup or (now - timezone.datetime.fromisoformat(last_popup)).days >= 1:
                    show_daily_cap_popup = True
                    request.session['last_daily_cap_popup'] = now.isoformat()
                context = {'tasks': tasks, 'completed_ids': completed_ids, 'show_daily_cap_popup': show_daily_cap_popup}
                return render(request, 'manual_tasks.html', context)
                # Non-premium: cap reached
            elif not user_profile.is_premium and today_earned + points > 1000:
                points = max(0, 1000 - today_earned)
                user_profile.balance += points
                user_profile.save()
                TaskCompletion.objects.create(user=request.user, manual_task=task)
            else:
                user_profile.balance += points
                user_profile.save()
                TaskCompletion.objects.create(user=request.user, manual_task=task)
        return redirect('manual_tasks')
    return render(request, 'manual_tasks.html', {'tasks': tasks, 'completed_ids': completed_ids})

# API VIEWS
from django.views.decorators.http import require_GET, require_POST

@login_required
@require_GET
def daily_task_api(request):
    today = datetime.date.today()
    daily_task = DailyTask.objects.filter(date=today).first()
    completed = TaskCompletion.objects.filter(user=request.user, manual_task__isnull=True, completed_at__date=today).exists()
    return JsonResponse({
        'question': daily_task.question if daily_task else None,
        'completed': completed,
    })

@login_required
@csrf_exempt
@require_POST
def submit_daily_task_api(request):
    today = datetime.date.today()
    daily_task = DailyTask.objects.filter(date=today).first()
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not daily_task:
        return JsonResponse({'error': 'No daily task today.'}, status=404)
    answer = request.POST.get('answer', '').strip()
    if TaskCompletion.objects.filter(user=request.user, manual_task__isnull=True, completed_at__date=today).exists():
        return JsonResponse({'error': 'Already completed.'}, status=400)
    if answer.lower() == daily_task.correct_answer.lower():
        # Award points with multiplier
        points = 50 * user_profile.get_earning_multiplier()
        user_profile.balance += points
        user_profile.save()
        TaskCompletion.objects.create(user=request.user, manual_task=None)
        return JsonResponse({'success': True, 'correct': True, 'points_awarded': points})
    return JsonResponse({'success': True, 'correct': False})

@login_required
@require_GET
def manual_tasks_api(request):
    tasks = ManualTask.objects.filter(is_active=True)
    completed_ids = set(TaskCompletion.objects.filter(user=request.user).values_list('manual_task_id', flat=True))
    data = [
        {
            'id': t.id,
            'description': t.description,
            'points': t.points,
            'completed': t.id in completed_ids,
        } for t in tasks
    ]
    return JsonResponse({'tasks': data})

@login_required
@csrf_exempt
@require_POST
def complete_manual_task_api(request):
    task_id = request.POST.get('task_id')
    task = get_object_or_404(ManualTask, id=task_id)
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if TaskCompletion.objects.filter(user=request.user, manual_task=task).exists():
        return JsonResponse({'error': 'Already completed.'}, status=400)
    points = task.points * user_profile.get_earning_multiplier()
    from .models import Transaction
    today = datetime.date.today()
    today_earned = Transaction.objects.filter(user=request.user, type='earn', created_at__date=today).aggregate(models.Sum('points'))['points__sum'] or 0
    if not user_profile.is_premium and today_earned >= 1000:
        return JsonResponse({'success': False, 'error': 'Daily points cap reached for non-premium users.'})
    elif not user_profile.is_premium and today_earned + points > 1000:
        points = max(0, 1000 - today_earned)
        user_profile.balance += points
        user_profile.save()
        TaskCompletion.objects.create(user=request.user, manual_task=task)
        return JsonResponse({'success': True, 'points': points})
    else:
        user_profile.balance += points
        user_profile.save()
        TaskCompletion.objects.create(user=request.user, manual_task=task)
        return JsonResponse({'success': True, 'points': points})

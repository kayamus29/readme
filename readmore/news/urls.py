from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from . import views_wallet

from . import views_news

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.CustomLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('wallet/', views_wallet.wallet, name='wallet'),
    path('news/', views_news.news_list, name='news_list'),
    path('news/article/<int:article_id>/', views_news.article_detail, name='article_detail'),
    path('mark_read/<int:article_id>/', views_news.mark_read, name='mark_read'),

    # Daily & Manual Tasks (HTML)
    path('daily-task/', views.daily_task_view, name='daily_task'),
    path('manual-tasks/', views.manual_tasks_view, name='manual_tasks'),
    path('profile/', views.profile_view, name='profile'),

    # Daily & Manual Tasks (API)
    path('api/daily-task/', views.daily_task_api, name='daily_task_api'),
    path('api/daily-task/submit/', views.submit_daily_task_api, name='submit_daily_task_api'),
    path('api/manual-tasks/', views.manual_tasks_api, name='manual_tasks_api'),
    path('api/manual-tasks/complete/', views.complete_manual_task_api, name='complete_manual_task_api'),
    path('terms/', views.terms_view, name='terms'),
]

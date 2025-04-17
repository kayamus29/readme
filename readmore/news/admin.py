from django.contrib import admin
from .models import UserProfile, NewsArticle, ReadHistory, DailyTask, ManualTask, TaskCompletion, CoinPurchaseRequest, CoinWithdrawalRequest
from django.utils import timezone
from django.contrib import admin

from .email_utils import send_user_notification

@admin.action(description="Approve selected purchase requests")
def approve_requests(modeladmin, request, queryset):
    for obj in queryset.filter(status='pending'):
        user_profile, _ = UserProfile.objects.get_or_create(user=obj.user)
        user_profile.coin_balance += obj.amount
        user_profile.save()
        from .models import Transaction
        Transaction.objects.create(
            user=obj.user,
            type='purchase',
            amount=obj.amount,
            coins=obj.amount,
            description=f'Approved coin purchase ({obj.amount} coins)'
        )
        obj.status = 'approved'
        obj.approved_at = timezone.now()
        obj.save()
        # Email notification
        if obj.user.email:
            send_user_notification(
                subject="Coin Purchase Approved",
                message=f"Your purchase of {obj.amount} coins has been approved and credited to your account.",
                recipient_email=obj.user.email
            )

@admin.action(description="Decline selected purchase requests")
def decline_requests(modeladmin, request, queryset):
    for obj in queryset.filter(status='pending'):
        obj.status = 'declined'
        obj.save()
        # Email notification
        if obj.user.email:
            send_user_notification(
                subject="Coin Purchase Declined",
                message=f"Your purchase of {obj.amount} coins has been declined. Please contact support for details.",
                recipient_email=obj.user.email
            )

@admin.register(CoinPurchaseRequest)
class CoinPurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'bnb_amount', 'wallet_address', 'status', 'created_at', 'approved_at')
    list_filter = ('status', 'created_at')
    actions = [approve_requests, decline_requests]

@admin.action(description="Approve selected withdrawal requests")
def approve_withdrawals(modeladmin, request, queryset):
    from django.utils import timezone
    for obj in queryset.filter(status='pending'):
        obj.status = 'approved'
        obj.approved_at = timezone.now()
        obj.save()
        # Email notification
        if obj.user.email:
            send_user_notification(
                subject="Withdrawal Approved",
                message=f"Your withdrawal request of {obj.amount} coins has been approved and will be processed shortly.",
                recipient_email=obj.user.email
            )

@admin.action(description="Decline selected withdrawal requests")
def decline_withdrawals(modeladmin, request, queryset):
    for obj in queryset.filter(status='pending'):
        obj.status = 'declined'
        obj.save()
        # Email notification
        if obj.user.email:
            send_user_notification(
                subject="Withdrawal Declined",
                message=f"Your withdrawal request of {obj.amount} coins has been declined. Please contact support for details.",
                recipient_email=obj.user.email
            )

@admin.register(CoinWithdrawalRequest)
class CoinWithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'wallet_address', 'status', 'created_at', 'approved_at')
    list_filter = ('status', 'created_at')
    actions = [approve_withdrawals, decline_withdrawals]

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'coin_balance', 'is_premium', 'wallet_address')
    list_editable = ('balance', 'coin_balance')
    search_fields = ('user__username', 'wallet_address')
admin.site.register(NewsArticle)
admin.site.register(ReadHistory)
admin.site.register(DailyTask)
admin.site.register(ManualTask)
admin.site.register(TaskCompletion)

# Register your models here.

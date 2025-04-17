from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_address = models.CharField(max_length=255, blank=True, null=True)
    balance = models.PositiveIntegerField(default=0)
    # Activation logic fields
    is_activated = models.BooleanField(default=False)
    followed_twitter = models.BooleanField(default=False)
    joined_telegram = models.BooleanField(default=False)
    subscribed_youtube = models.BooleanField(default=False)
    referred_count = models.PositiveIntegerField(default=0)
    referral_code = models.CharField(max_length=32, unique=True, blank=True, null=True)
    referred_by = models.CharField(max_length=32, blank=True, null=True)
    is_premium = models.BooleanField(default=False, help_text="Premium members earn double points.")
    coin_balance = models.PositiveIntegerField(default=0, help_text="User's coin balance.")

    def check_activation(self):
        """Check if user has met all activation requirements."""
        return (
            self.followed_twitter and
            self.joined_telegram and
            self.subscribed_youtube and
            self.referred_count >= 2
        )

    def activate(self):
        if self.check_activation():
            self.is_activated = True
            self.save()
        return self.is_activated

    def get_earning_multiplier(self):
        return 2 if self.is_premium else 1

    def get_rank(self):
        # Example thresholds for 10 ranks (customize as needed)
        thresholds = [0, 100, 250, 500, 1000, 2000, 3500, 5000, 7500, 10000]
        for i, threshold in enumerate(thresholds, 1):
            if self.balance < threshold:
                return max(1, i-1)
        return 10

    def save(self, *args, **kwargs):
        if not self.referral_code:
            import random, string
            while True:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not UserProfile.objects.filter(referral_code=code).exists():
                    self.referral_code = code
                    break
        super().save(*args, **kwargs)

    @property
    def safe_referral_code(self):
        return self.referral_code or ''

    def __str__(self):
        return self.user.username

class NewsArticle(models.Model):
    title = models.CharField(max_length=512)
    url = models.URLField(unique=True)
    source = models.CharField(max_length=255)
    published_at = models.DateTimeField()
    summary = models.TextField(blank=True)
    # Add more fields as needed

    def __str__(self):
        return self.title

class ReadHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')

class CoinPurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    bnb_amount = models.DecimalField(max_digits=18, decimal_places=6)
    wallet_address = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} coins ({self.status})"

class CoinWithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    wallet_address = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} requests {self.amount} coins ({self.status})"

    def clean(self):
        if self.amount < 30:
            raise ValidationError("Minimum withdrawal amount is 30 coins.")

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('purchase', 'Coin Purchase'),
        ('convert', 'Points to Coin'),
        ('earn', 'Earned Points'),
        ('spend', 'Spent Points'),
        ('other', 'Other'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=16, choices=TRANSACTION_TYPES)
    amount = models.PositiveIntegerField()
    points = models.IntegerField(default=0)
    coins = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.amount}"
class DailyTask(models.Model):
    question = models.CharField(max_length=512)
    correct_answer = models.CharField(max_length=255)
    date = models.DateField(unique=True)

    def __str__(self):
        return f"Daily Task {self.date}"

class ManualTask(models.Model):
    description = models.CharField(max_length=512)
    button_url = models.URLField(blank=True, null=True, help_text="URL for the task button (e.g., https://twitter.com/yourpage)")
    points = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.description

class TaskCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    manual_task = models.ForeignKey(ManualTask, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'manual_task')

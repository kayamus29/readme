from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    def clean(self):
        username_or_email = self.cleaned_data.get('username') or self.cleaned_data.get('login')
        password = self.cleaned_data.get('password')
        if username_or_email and password:
            try:
                user = User.objects.get(email=username_or_email)
                username = user.username
            except User.DoesNotExist:
                username = username_or_email
            self.cleaned_data['username'] = username
        return super().clean()

class CustomUserCreationForm(UserCreationForm):
    referral_code = forms.CharField(
        max_length=32,
        required=False,
        label='Referral Code (optional)',
        widget=forms.TextInput(attrs={'placeholder': 'Referral Code'})
    )

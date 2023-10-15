from siteuser.models import CustomUser
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomerSignUp
from django import forms
from django.contrib.auth import get_user_model
from siteuser.models import SiteUser

CustomUser = get_user_model()
class CustomerSignUpForm(forms.Form):
    email = forms.EmailField(required=True, label="Email", widget=forms.EmailInput(
        attrs={'placeholder': 'Enter your Email'}))
    password1 = forms.CharField(required=True, label="Password", widget=forms.PasswordInput(
        attrs={'placeholder': 'password'}))
    password2 = forms.CharField(required=True, label="Password", widget=forms.PasswordInput(
        attrs={'placeholder': 'password'}))

    def clean(self):
        data = self.cleaned_data
        email = data.get("email", None).strip()
        password1 = data.get('password1', None).strip()
        password2 = data.get('password2', None).strip()

        User = get_user_model()
        if User.objects.filter(email=email).exists():
            self.add_error('email', 'Email already registered.')

        if password1 and password2 and password1 != password2:
            self.add_error('password1', "Passwords do not match")

        if SiteUser.objects.filter(screen_name=email).exists():
            self.add_error('screen_name', 'Display name already taken.')
class CustomerLoginForm(forms.Form):
    email = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100)

class UpdateCustomerForm(forms.ModelForm):
    # information = forms.CharField(widget=forms.Textarea(attrs={"rows": 4, "cols": 10})
    information = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = CustomerSignUp
        exclude = ['user']

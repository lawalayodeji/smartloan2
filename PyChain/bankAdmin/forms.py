
from django import forms
from loanApp.models import loanCategory


class LoanCategoryForm(forms.ModelForm):
    class Meta:
        model = loanCategory
        fields = ('loan_name',)


class AdminLoginForm(forms.Form):
    email = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100)
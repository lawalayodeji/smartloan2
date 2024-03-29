from django.db import models
import uuid
from siteuser.models import CustomUser

# Create your models here.


class loanCategory(models.Model):
    loan_name = models.CharField(max_length=250)
    creation_date = models.DateField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.loan_name


class loanRequest(models.Model):
    customer = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='loan_customer')
    category = models.ForeignKey(
        loanCategory, on_delete=models.CASCADE, null=True)
    request_date = models.DateField(auto_now_add=True)
    status_date = models.CharField(
        max_length=150, null=True, blank=True, default=None)
    reason = models.TextField()
    status = models.CharField(max_length=100, default='pending')
    amount = models.PositiveIntegerField(default=0)
    year = models.PositiveIntegerField(default=1)
    paid_loan = models.BooleanField(default=False)    
    def __str__(self):
        return self.customer.email

class CustomerLoan(models.Model):
    customer = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='loan_user')
    total_loan = models.PositiveIntegerField(default=0)
    payable_loan = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.customer.email

class loanTransaction(models.Model):
    customer = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='transaction_customer')

    transaction = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.PositiveIntegerField(default=0)
    payment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.customer.email

from django.db import models
from siteuser.models import CustomUser

# Create your models here.


class CustomerSignUp(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='customer')
    first_name = models.CharField(max_length=250, blank=False)
    last_name = models.CharField(max_length=250, blank=False)
    address = models.CharField(
        max_length=250, default='lagos, Nigeria', blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profile_pic', )
    designation = models.CharField(max_length=100, blank=False)
    phone = models.IntegerField(blank=True, null=True)
    information = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.email


# class CustomerLogin(models.Model):
#     username = models.CharField(max_length=250, blank=False, null=False)
#     password = models.PasswordField(max_length=100, blank=False)

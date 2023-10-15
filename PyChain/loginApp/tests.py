from django.test import TestCase

# Create your tests here.

from siteuser.models import  CustomUser
# from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password


def authenticate(email=None, password=None):
    myuser = CustomUser.objects.filter(email=email)


    if myuser.exists():
        myuser1 = CustomUser.objects.get(email=email)

        pwd_valid = check_password(password, myuser1.password)
        if pwd_valid:
            return myuser
    return None
# from django.db import models

# # Create your models here.
# from siteuser.models import  CustomUser
# # from django.contrib.auth.backends import BaseBackend
# from django.contrib.auth.hashers import check_password


# def authenticate(self, email=None, password=None):
#     myuser = CustomUser.objects.filter(email=email)


#     if myuser.exists():
#         pwd_valid = check_password(password, myuser.password)
#         if pwd_valid:
#             return myuser
#     return None

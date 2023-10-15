from django.shortcuts import render
from django.contrib.auth import authenticate,  login, logout
from .forms import CustomerSignUpForm, CustomerLoginForm, UpdateCustomerForm
from django.shortcuts import redirect
from .models import CustomerSignUp
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
from siteuser.models import CustomUser, SiteUser, Wallet
from siteuser.walletInit import walletInitGen
from blockchain.blockchain_client import COINBASE
from django.db.models import Sum

# from loginApp.tests import authenticate
# Create your views here.


def sign_up_view(request):
    error = ''
    if request.user.is_authenticated:

        return HttpResponseRedirect(reverse('home'))

    form = CustomerSignUpForm()
    if request.method == 'POST':

        form = CustomerSignUpForm(request.POST)
        # print(form.cleaned_data['username'])
        if form.is_valid():
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            user2 = CustomUser(email=email)
            user2.set_password(password1)
            user2.is_active=True
            user2.save()
            user_profile = CustomerSignUp(user=user2)
            user_profile.save()

            new_user = SiteUser(user=user2, screen_name=email)
            new_user.save()
            private_key, public_key = walletInitGen()

            # get balance of coins in the system
            SUM_COINS = Wallet.objects.aggregate(total_balance=Sum('balance'))['total_balance']
            # If no wallet instance has been created, the balance returns None
            if SUM_COINS == None:
                SUM_COINS = 0.00
            if SUM_COINS < COINBASE:
                balance = 50.00
            else:
                balance = 0.00
            Wallet.objects.create(alias="Rename (30 characters)",
            owner=new_user, private_key=private_key, balance=balance, public_key=public_key)
            user = authenticate(request, email=email, password=password1)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('home'))

            return HttpResponseRedirect(reverse('login_App:login_customer'))

        else:
            if CustomUser.objects.filter(email=request.POST['email']).exists():
                error = 'customer already exists'

            else:
                error = 'Your password is not strong enough or both password must be same'
        

    return render(request, 'loginApp/signup.html', context={'form': form, 'user': "Customer Register", 'error': error})


def mylogin_view(request):
    form = CustomerLoginForm()
    if request.method == 'POST':
        form = CustomerLoginForm(data=request.POST)
        # username = request.POST['username']
        # password = request.POST['password']
        # print(username, password)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            print(password)
            user = authenticate(request,email=email, password=password)
            print(user)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('home'))
            return render(request, 'loginApp/login.html', context={'form': form, 'user': "Customer Login", 'error': 'Invalid  email or password'})
            

        else:
            return render(request, 'loginApp/login.html', context={'form': form, 'user': "Customer Login", 'error': 'Invalid  form email or password'})
    return render(request, 'loginApp/login.html', context={'form': form, 'user': "Customer Login"})


@login_required()
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


@login_required(login_url='/account/login-customer')
def edit_customer(request):
    customer = CustomerSignUp.objects.get(user=request.user)
    form = UpdateCustomerForm(instance=customer)
    if request.method == 'POST':

        form = UpdateCustomerForm(
            request.POST, request.FILES, instance=customer)
        if form.is_valid:
            customer = form.save(commit=False)
            customer.save()
            return HttpResponseRedirect(reverse('home'))
    # return HttpResponseRedirect(reverse('home'))
    return render(request, 'loginApp/edit.html', context={'form': form})

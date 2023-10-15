from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from bankAdmin.forms import AdminLoginForm
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from loanApp.models import loanCategory, loanRequest, CustomerLoan,loanTransaction
from .forms import LoanCategoryForm
from siteuser.models import SiteUser, CustomUser,Wallet
from datetime import date
from siteuser.walletInit import walletInitGen
from blockchain.blockchain_client import  COINBASE,Transaction
from django.conf import settings
from django.db.models import Sum
from django.contrib import messages


BLOCKCHAIN = settings.BLOCKCHAIN


def superuser_login_view(request):
    form = AdminLoginForm()
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))
    else:
        if request.method == 'POST':
            form = AdminLoginForm(request.POST)

            if form.is_valid():
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']


                myuser = authenticate(
                    request, email=email, password=password)
                
                if myuser is not None:

                    if myuser.is_admin:
                        if SiteUser.objects.filter(user=myuser).exists() == False:
                            new_user = SiteUser(user=myuser, screen_name=email)
                            new_user.save()
                            private_key, public_key = walletInitGen()

                            # get balance of coins in the system
                            SUM_COINS = Wallet.objects.aggregate(total_balance=Sum('balance'))['total_balance']
                            # If no wallet instance has been created, the balance returns None
                            if SUM_COINS == None:
                                SUM_COINS = 0.00
                            if SUM_COINS < COINBASE:
                                balance = 2000.00
                            else:
                                balance = 0.00
                            Wallet.objects.create(alias="Rename (30 characters)",
                            owner=new_user, private_key=private_key, balance=balance, public_key=public_key)
                        login(request, myuser)
                        return HttpResponseRedirect(reverse('bankAdmin:dashboard'))
                    else:
                        return render(request, 'admin/adminLogin.html', context={'form': form, 'error': "You are not Super User"})

            else:

                return render(request, 'admin/adminLogin.html', context={'form': form, 'error': "Invalid email or Password "})
    return render(request, './admin/adminLogin.html', context={'form': form, 'user': "Admin Login"})


# @user_passes_test(lambda u: u.is_superuser)
@staff_member_required(login_url='/bankManger/admin-login')
def dashboard(request):

    totalCustomer = SiteUser.objects.all().count(),
    requestLoan = loanRequest.objects.all().filter(status='pending').count(),
    approved = loanRequest.objects.all().filter(status='approved').count(),
    rejected = loanRequest.objects.all().filter(status='rejected').count(),
    totalLoan = CustomerLoan.objects.aggregate(Sum('total_loan'))[
        'total_loan__sum'],
    totalPayable = CustomerLoan.objects.aggregate(
        Sum('payable_loan'))['payable_loan__sum'],
    totalPaid = loanTransaction.objects.aggregate(Sum('payment'))[
        'payment__sum'],

    dict = {
        'totalCustomer': totalCustomer[0],
        'request': requestLoan[0],
        'approved': approved[0],
        'rejected': rejected[0],
        'totalLoan': totalLoan[0],
        'totalPayable': totalPayable[0],
        'totalPaid': totalPaid[0],

    }
    print(dict)

    return render(request, 'admin/dashboard.html', context=dict)


@staff_member_required(login_url='/bankManger/admin-login')
def add_category(request):
    form = LoanCategoryForm()
    if request.method == 'POST':
        form = LoanCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('bankAdmin:dashboard')
    return render(request, 'admin/admin_add_category.html', {'form': form})


@staff_member_required(login_url='/bankManger/admin-login')
def total_users(request):
    users = SiteUser.objects.all()

    return render(request, 'admin/customer.html', context={'users': users})


@staff_member_required(login_url='/bankManger/admin-login')
def user_remove(request, pk):
    SiteUser.objects.get(id=pk).delete()
    user = CustomUser.objects.get(id=pk)
    user.delete()
    return HttpResponseRedirect('/bankManger/users/')
    # return redirect('bankAdmin:users')


@staff_member_required(login_url='/bankManger/admin-login')
def loan_request(request):
    loanrequest = loanRequest.objects.filter(status='pending')
    return render(request, 'admin/request_user.html', context={'loanrequest': loanrequest})


@staff_member_required(login_url='/bankManger/admin-login')
def approved_request(request, id):
    today = date.today()
    status_date = today.strftime("%B %d, %Y")
    loan_obj = loanRequest.objects.get(id=id)
    loan_obj.status_date = status_date
    loan_obj.save()
    year = loan_obj.year

    mycustomer = loanRequest.objects.get(id=id)
    approved_customer = mycustomer.customer
    my_user = SiteUser.objects.filter(user=request.user)
    if my_user.exists():
        admin_wallet_1 = Wallet.objects.filter(owner=my_user[0])
        if admin_wallet_1.exists():
            admin_wallet = admin_wallet_1[0]
            convertion = 0.00000000000025
            pr_key = admin_wallet.private_key
            pb_key = admin_wallet.public_key
            client_siteuser = SiteUser.objects.filter(user=approved_customer)[0]
            client_wallet = Wallet.objects.filter(owner=client_siteuser)[0]

            re_pb_key = client_wallet.public_key
            amount = mycustomer.amount
            mycoin = amount * convertion
            transaction_object = Transaction(pb_key, pr_key, re_pb_key, mycoin)
            transaction = transaction_object.to_dict()
            signature = transaction_object.sign_transaction()
            verify = BLOCKCHAIN.verify_transaction_signature(pb_key, signature, transaction)
            if verify:
                BLOCKCHAIN.add_transaction_to_current_array(pb_key, re_pb_key, mycoin, signature)
                last_block = BLOCKCHAIN.last_block()
                nonce = BLOCKCHAIN.proof_of_work()

                # reward for finding proof
                BLOCKCHAIN.reward_miner(BLOCKCHAIN.node_id)

                # forge new block and add to chain
                previous_hash = BLOCKCHAIN.hash(last_block)
                BLOCKCHAIN.forge_block_and_add_to_chain(nonce, previous_hash)
                admin_wallet.balance -= mycoin
                admin_wallet.save()
                client_wallet.balance += mycoin
                client_wallet.save()
                print("doneee")

                messages.success(request, "Transaction signature verified successfully and transaction stacked for 'blocking'.")
            else:
                messages.error(request, "Transaction rejected")


    if CustomerLoan.objects.filter(customer=approved_customer).exists():
        PreviousAmount = CustomerLoan.objects.get(
        customer=approved_customer).total_loan
        PreviousPayable = CustomerLoan.objects.get(
            customer=approved_customer).payable_loan

        # update balance
        CustomerLoan.objects.filter(
            customer=approved_customer).update(total_loan=int(PreviousAmount)+int(loan_obj.amount))
        CustomerLoan.objects.filter(
            customer=approved_customer).update(payable_loan=int(PreviousPayable)+int(loan_obj.amount)+int(loan_obj.amount)*0.12*int(year))

    else:

        # request customer

        # CustomerLoan object create
        save_loan = CustomerLoan()

        save_loan.customer = approved_customer
        save_loan.total_loan = int(loan_obj.amount)
        save_loan.payable_loan = int(
            loan_obj.amount)+int(loan_obj.amount)*0.12*int(year)
        save_loan.save()

    loanRequest.objects.filter(id=id).update(status='approved')
    loanrequest = loanRequest.objects.filter(status='pending')
    print(loanrequest)
    print("yes")
    return render(request, 'admin/request_user.html', context={'loanrequest': loanrequest})


@staff_member_required(login_url='/bankManger/admin-login')
def rejected_request(request, id):

    today = date.today()
    status_date = today.strftime("%B %d, %Y")
    loan_obj = loanRequest.objects.get(id=id)
    loan_obj.status_date = status_date
    loan_obj.save()
    # rejected_customer = loanRequest.objects.get(id=id).customer
    # print(rejected_customer)
    loanRequest.objects.filter(id=id).update(status='rejected')
    loanrequest = loanRequest.objects.filter(status='pending')
    return render(request, 'admin/request_user.html', context={'loanrequest': loanrequest})


@staff_member_required(login_url='/bankManger/admin-login')
def approved_loan(request):
    # print(datetime.now())
    approvedLoan = loanRequest.objects.filter(status='approved')
    return render(request, 'admin/approved_loan.html', context={'approvedLoan': approvedLoan})


@staff_member_required(login_url='/bankManger/admin-login')
def rejected_loan(request):
    rejectedLoan = loanRequest.objects.filter(status='rejected')
    return render(request, 'admin/rejected_loan.html', context={'rejectedLoan': rejectedLoan})


@staff_member_required(login_url='/bankManger/admin-login')
def transaction_loan(request):
    transactions = loanTransaction.objects.all()
    return render(request, 'admin/transaction.html', context={'transactions': transactions})

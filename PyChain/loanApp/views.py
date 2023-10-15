from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import LoanRequestForm, LoanTransactionForm
from .models import loanRequest, loanTransaction, CustomerLoan
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, HttpResponse
from siteuser.models import Wallet, SiteUser
from django.db.models import Sum
from blockchain.blockchain_client import Transaction, COINBASE, MINING_DIFFICULTY, MINING_REWARD, MINABLE_TRANSACTIONS
from django.conf import settings

# Create your views here.

BLOCKCHAIN = settings.BLOCKCHAIN

# @login_required(login_url='/account/login-customer')
def home(request):

    return render(request, 'home.html', context={})


@login_required(login_url='/account/login-customer')
def LoanRequest(request):

    form = LoanRequestForm()

    if request.method == 'POST':
        form = LoanRequestForm(request.POST)

        if form.is_valid():
            loan_obj = form.save(commit=False)
            loan_obj.customer = request.user
            loan_obj.save()
            return redirect('/')

    return render(request, 'loanApp/loanrequest.html', context={'form': form})

    # reason = request.POST.get('reason')
    # amount = request.POST.get('amount')
    # category = request.POST.get('category')
    # year = request.POST.get('year')
    # customer = request.user

    # loan_request = LoanRequest(request)
    # loan_request.customer = customer
    # loan_request.save()
    # if form.is_valid():
    #     loan_request = form.save(commit=False)
    #     loan_request.customer = request.user
    #     print(loan_request)
    #     return redirect('/')


@login_required(login_url='/account/login-customer')
def LoanPayment(request):
    form = LoanTransactionForm()
    loan_r = loanRequest.objects.filter(customer = request.user, status="approved",paid_loan=False)
    
    # if request.method == 'POST':
    #     form = LoanTransactionForm(request.POST)
    #     if form.is_valid():
    #         payment = form.save(commit=False)
    #         payment.customer = request.user
    #         payment.save()
    #         # pay_save = loanTransaction()
    #         return redirect('/')

    return render(request, 'loanApp/payment.html', context={'loan_obj': loan_r})


def makePayment(request, id):
    loan_credit = loanRequest.objects.get(id=id)
    loan_amount = (loan_credit.amount*0.12)+loan_credit.amount
    mySiteuser = SiteUser.objects.filter(user=request.user)
    mytransact = loanTransaction()
    mytransact.customer = request.user
    mytransact.payment = loan_amount
    mytransact.save()
    mycoin = loan_amount *0.00000000000025
    valid_wallet = None
    err=  "error"
    for mysite in mySiteuser:
        wallet_id = Wallet.objects.get(owner=mysite)
        if wallet_id.balance >= loan_amount:
            valid_wallet = wallet_id
            break
    admin_wallet_id = Wallet.objects.filter(admin_wallet=True)[0]

    if valid_wallet is not None:
        pr_key = valid_wallet.private_key
        pb_key = valid_wallet.public_key
        re_public_key = admin_wallet_id.public_key
        transaction_object = Transaction(pb_key, pr_key, re_public_key, mycoin)
        transaction = transaction_object.to_dict()
        signature = transaction_object.sign_transaction()

        signature = transaction_object.sign_transaction()
        verify = BLOCKCHAIN.verify_transaction_signature(pb_key, signature, transaction)
        if verify:
            BLOCKCHAIN.add_transaction_to_current_array(pb_key, re_public_key, mycoin, signature)
            last_block = BLOCKCHAIN.last_block()
            nonce = BLOCKCHAIN.proof_of_work()

            # reward for finding proof
            BLOCKCHAIN.reward_miner(BLOCKCHAIN.node_id)

            # forge new block and add to chain
            previous_hash = BLOCKCHAIN.hash(last_block)
            BLOCKCHAIN.forge_block_and_add_to_chain(nonce, previous_hash)
            admin_wallet_id.balance += mycoin
            admin_wallet_id.save()
            valid_wallet.balance -= mycoin
            valid_wallet.save()
            loan_credit.paid_loan = True
            loan_credit.save()
            err = "Transfer Successful!"
    else:
        err = "Your  wallet balance is low!"


    return render(request, 'loanApp/confirmPay.html', context={'err': err})


@login_required(login_url='/account/login-customer')
def UserTransaction(request):
    transactions = loanTransaction.objects.filter(
        customer=request.user)
    return render(request, 'loanApp/user_transaction.html', context={'transactions': transactions})


@login_required(login_url='/account/login-customer')
def UserLoanHistory(request):
    loans = loanRequest.objects.filter(
        customer=request.user)
    return render(request, 'loanApp/user_loan_history.html', context={'loans': loans})


@login_required(login_url='/account/login-customer')
def UserDashboard(request):

    requestLoan = loanRequest.objects.all().filter(
        customer=request.user).count(),
    approved = loanRequest.objects.all().filter(
        customer=request.user).filter(status='approved').count(),
    rejected = loanRequest.objects.all().filter(
        customer=request.user).filter(status='rejected').count(),
    totalLoan = CustomerLoan.objects.filter(customer=request.user).aggregate(Sum('total_loan'))[
        'total_loan__sum'],
    totalPayable = CustomerLoan.objects.filter(customer=request.user).aggregate(
        Sum('payable_loan'))['payable_loan__sum'],
    totalPaid = loanRequest.objects.all().filter(
        customer=request.user).filter(status='approved',paid_loan=True).aggregate(Sum('amount'))[
        'amount__sum'],
    
    dict = {
        'request': requestLoan[0],
        'approved': approved[0],
        'rejected': rejected[0],
        'totalLoan': totalLoan[0],
        'totalPayable': totalPayable[0],
        'totalPaid': totalPaid[0],
        

    }

    return render(request, 'loanApp/user_dashboard.html', context=dict)


def error_404_view(request, exception):
    print("not found")
    return render(request, 'notFound.html')

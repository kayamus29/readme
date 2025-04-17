from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import UserProfile

@login_required
def wallet(request):
    user_profile = UserProfile.objects.get(user=request.user)
    from .models import CoinPurchaseRequest
    buy_success = False
    bought_amount = 0
    # Show only the latest request (pending or approved)
    latest_request = CoinPurchaseRequest.objects.filter(user=request.user).order_by('-created_at').first()
    request_status = None
    request_amount = None
    if latest_request:
        if latest_request.status == 'pending':
            request_status = 'pending'
            request_amount = latest_request.amount
        elif latest_request.status == 'approved':
            if request.session.get('last_approved_purchase_id') != latest_request.id:
                request_status = 'approved'
                request_amount = latest_request.amount
                request.session['last_approved_purchase_id'] = latest_request.id

    withdraw_success = False
    withdraw_error = ''
    if request.method == 'POST':
        if 'withdraw_coins' in request.POST:
            try:
                amount = int(request.POST.get('withdraw_amount', 0))
                if amount < 30:
                    withdraw_error = 'Minimum withdrawal is 30 coins.'
                elif amount > user_profile.coin_balance:
                    withdraw_error = 'You do not have enough coins.'
                else:
                    from .models import CoinWithdrawalRequest
                    CoinWithdrawalRequest.objects.create(
                        user=request.user,
                        amount=amount,
                        wallet_address=user_profile.wallet_address or '',
                        status='pending',
                    )
                    user_profile.coin_balance -= amount
                    user_profile.save()
                    withdraw_success = True
                    return redirect('wallet')
            except (ValueError, TypeError):
                withdraw_error = 'Invalid withdrawal amount.'
        elif 'buy_coins' in request.POST:
            try:
                amount = int(request.POST.get('buy_amount', 0))
                if amount > 0:
                    bnb_amount = round(amount * 0.001, 6)
                    CoinPurchaseRequest.objects.create(
                        user=request.user,
                        amount=amount,
                        bnb_amount=bnb_amount,
                        wallet_address=user_profile.wallet_address or '',
                        status='pending',
                    )
                    buy_success = True
                    bought_amount = amount
                    request_status = 'pending'
                    request_amount = amount
                    return redirect('wallet')
            except (ValueError, TypeError):
                pass
        else:
            wallet_address = request.POST.get('wallet_address')
            if wallet_address:
                user_profile.wallet_address = wallet_address
                user_profile.save()
                return redirect('wallet')
    # Conversion rate (set in code)
    CONVERSION_RATE = 1000  # points per coin (premium standard)

    from .models import Transaction
    # Automatic conversion
    coins_to_credit = user_profile.balance // CONVERSION_RATE
    if coins_to_credit > 0:
        user_profile.balance -= coins_to_credit * CONVERSION_RATE
        user_profile.coin_balance += coins_to_credit
        user_profile.save()
        Transaction.objects.create(
            user=request.user,
            type='convert',
            amount=coins_to_credit,
            points=-coins_to_credit * CONVERSION_RATE,
            coins=coins_to_credit,
            description=f'Automatically converted {coins_to_credit * CONVERSION_RATE} points to {coins_to_credit} coins.'
        )
    # If less than 1000 points, no conversion occurs

    # Transaction history
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:20]
    from .models import CoinWithdrawalRequest
    withdrawals = CoinWithdrawalRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'wallet.html', {
        'withdraw_success': withdraw_success,
        'withdraw_error': withdraw_error,
        'withdrawals': withdrawals,
        'user_profile': user_profile,
        'buy_success': buy_success,
        'bought_amount': bought_amount,
        'request_status': request_status,
        'request_amount': request_amount,
        'transactions': transactions,
        'conversion_rate': CONVERSION_RATE,
    })

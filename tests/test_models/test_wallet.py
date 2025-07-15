from decimal import Decimal

import pytest

from apps.account.models import Transaction, Wallet
from apps.common.exceptions import ValidationError


@pytest.mark.django_db
def test_wallet_str_returns_label():
    wallet = Wallet.objects.create(label="My Wallet")
    assert str(wallet) == "My Wallet"


@pytest.mark.django_db
def test_wallet_balance_no_transactions():
    wallet = Wallet.objects.create(label="Empty Wallet")
    assert wallet.balance == Decimal("0")


@pytest.mark.django_db
def test_wallet_balance_sum_of_transactions():
    wallet = Wallet.objects.create(label="Wallet with Tx")
    Transaction.objects.create(wallet=wallet, txid="tx1", amount=Decimal("10.5"))
    Transaction.objects.create(wallet=wallet, txid="tx2", amount=Decimal("-3.25"))
    Transaction.objects.create(wallet=wallet, txid="tx3", amount=Decimal("2.75"))

    expected_balance = Decimal("10.5") + Decimal("-3.25") + Decimal("2.75")
    assert wallet.balance == expected_balance


@pytest.mark.django_db
def test_update_balance_passes_for_non_negative():
    wallet = Wallet.objects.create(label="Wallet")
    Transaction.objects.create(wallet=wallet, txid="tx1", amount=Decimal("5.0"))
    Transaction.objects.create(wallet=wallet, txid="tx2", amount=Decimal("-2.0"))

    balance = wallet.update_balance()
    assert balance == Decimal("3.0")


@pytest.mark.django_db
def test_transaction_prevents_negative_wallet_balance():
    wallet = Wallet.objects.create(label="Test Wallet")

    Transaction.objects.create(wallet=wallet, txid="tx1", amount=Decimal("10.0"))

    tx2 = Transaction(wallet=wallet, txid="tx2", amount=Decimal("-20.0"))

    with pytest.raises(ValidationError) as exc:
        tx2.full_clean()

    assert "Wallet balance cannot become negative." in str(exc.value)

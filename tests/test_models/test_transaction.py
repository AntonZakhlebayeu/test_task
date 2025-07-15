from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError

import pytest

from apps.account.models import Transaction, Wallet
from apps.common.exceptions import ValidationError as CustomValidationError


@pytest.mark.django_db
def test_transaction_creation_success():
    wallet = Wallet.objects.create(label="Test Wallet")
    tx = Transaction.objects.create(wallet=wallet, txid="tx123", amount=Decimal("100.00"))

    assert tx.wallet == wallet
    assert tx.amount == Decimal("100.00")
    assert tx.txid == "tx123"


@pytest.mark.django_db
def test_transaction_negative_balance_disallowed():
    wallet = Wallet.objects.create(label="Empty Wallet")
    tx = Transaction(wallet=wallet, txid="tx456", amount=Decimal("-10.00"))

    with pytest.raises(CustomValidationError) as exc:
        tx.full_clean()

    assert "Wallet balance cannot become negative" in str(exc.value)


@pytest.mark.django_db
def test_transaction_update_balance_diff():
    wallet = Wallet.objects.create(label="Wallet")
    tx = Transaction.objects.create(wallet=wallet, txid="tx789", amount=Decimal("100.00"))

    tx.amount = Decimal("50.00")
    tx.save()

    assert wallet.balance == Decimal("50.00")


@pytest.mark.django_db
def test_transaction_txid_unique():
    wallet = Wallet.objects.create(label="Wallet")
    Transaction.objects.create(wallet=wallet, txid="unique123", amount=Decimal("10.00"))

    with pytest.raises(DjangoValidationError):
        Transaction.objects.create(wallet=wallet, txid="unique123", amount=Decimal("5.00"))


@pytest.mark.django_db
def test_transaction_soft_delete():
    wallet = Wallet.objects.create(label="Wallet")
    tx = Transaction.objects.create(wallet=wallet, txid="txdel", amount=Decimal("5.00"))

    tx.delete()

    assert tx.is_deleted is True
    assert Transaction.objects.count() == 0
    assert Transaction.all_objects.count() == 1

from decimal import Decimal
from uuid import uuid4

import pytest

from apps.account.exceptions import SameWalletException, WalletNotFoundError
from apps.account.models import Transaction, Wallet
from apps.account.services.wallet import WalletService
from apps.common.exceptions import BalanceNegativeError, ValidationError


@pytest.mark.django_db
def test_apply_cash_flow_deposit():
    wallet = Wallet.objects.create(label="My Wallet")
    WalletService.apply_cash_flow(wallet_id=str(wallet.id), amount=Decimal("50.00"))

    wallet.refresh_from_db()
    assert wallet.balance == Decimal("50.00")
    assert Transaction.objects.filter(wallet=wallet, amount=Decimal("50.00")).exists()


@pytest.mark.django_db
def test_apply_cash_flow_withdrawal_allowed():
    wallet = Wallet.objects.create(label="My Wallet")
    WalletService.apply_cash_flow(wallet_id=str(wallet.id), amount=Decimal("100.00"))

    WalletService.apply_cash_flow(wallet_id=str(wallet.id), amount=Decimal("-50.00"))

    wallet.refresh_from_db()
    assert wallet.balance == Decimal("50.00")


@pytest.mark.django_db
def test_apply_cash_flow_withdrawal_disallowed_negative_balance():
    wallet = Wallet.objects.create(label="My Wallet")

    with pytest.raises(BalanceNegativeError):
        WalletService.apply_cash_flow(wallet_id=str(wallet.id), amount=Decimal("-10.00"))


@pytest.mark.django_db
def test_apply_cash_flow_wallet_not_found():
    with pytest.raises(WalletNotFoundError):
        WalletService.apply_cash_flow(wallet_id=str(uuid4()), amount=Decimal("10.00"))


@pytest.mark.django_db
def test_transfer_success():
    source = Wallet.objects.create(label="Source")
    dest = Wallet.objects.create(label="Destination")

    WalletService.apply_cash_flow(wallet_id=str(source.id), amount=Decimal("100.00"))

    source_before = source.balance
    dest_before = dest.balance

    source_updated, dest_updated = WalletService.transfer(
        source_id=str(source.id),
        dest_id=str(dest.id),
        amount=Decimal("40.00"),
    )

    source_updated.refresh_from_db()
    dest_updated.refresh_from_db()

    assert source_updated.balance == source_before - Decimal("40.00")
    assert dest_updated.balance == dest_before + Decimal("40.00")


@pytest.mark.django_db
def test_transfer_negative_amount_raises():
    source = Wallet.objects.create(label="Source")
    dest = Wallet.objects.create(label="Destination")

    with pytest.raises(BalanceNegativeError):
        WalletService.transfer(
            source_id=str(source.id), dest_id=str(dest.id), amount=Decimal("-5.00")
        )


@pytest.mark.django_db
def test_transfer_insufficient_funds_raises():
    source = Wallet.objects.create(label="Source")
    dest = Wallet.objects.create(label="Destination")

    with pytest.raises(ValidationError):
        WalletService.transfer(
            source_id=str(source.id), dest_id=str(dest.id), amount=Decimal("10.00")
        )


@pytest.mark.django_db
def test_transfer_to_the_same_wallet_raises():
    source = Wallet.objects.create(label="Source")

    with pytest.raises(SameWalletException):
        WalletService.transfer(
            source_id=str(source.id), dest_id=str(source.id), amount=Decimal("10.00")
        )


@pytest.mark.django_db
def test_transfer_wallet_not_found_raises():
    source = Wallet.objects.create(label="Source")

    missing_id = str(uuid4())

    with pytest.raises(WalletNotFoundError) as exc:
        WalletService.transfer(
            source_id=str(source.id), dest_id=missing_id, amount=Decimal("10.00")
        )
    assert missing_id in str(exc.value)

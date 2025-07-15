from django.db import models, transaction

from apps.account.models.wallet import Wallet
from apps.common.exceptions import ValidationError
from apps.common.managers import SoftDeleteManager
from apps.common.mixins import SafeSaveMixin, SoftDeleteMixin, TimestampMixin, UUIDMixin


class Transaction(UUIDMixin, TimestampMixin, SafeSaveMixin, SoftDeleteMixin):
    """
    Represents a financial transaction linked to a Wallet.

    Attributes:
      - wallet: ForeignKey to the Wallet this transaction belongs to.
      - txid: Unique transaction identifier string, indexed for fast lookups.
      - amount: Decimal amount of the transaction, supporting high precision.

    Constraints & Behavior:
      - Ensures the transaction belongs to a wallet.
      - Validates that applying the transaction amount does not cause the wallet's
        balance to become negative.
      - On save, performs full validation and atomic database save to maintain consistency.
      - Supports soft deletion and UUID primary key via mixins.

    Meta:
      - Adds database indexes on 'txid' and combined 'wallet' and 'amount' for performance.
    """

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions", db_index=True
    )
    txid = models.CharField(max_length=255, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=36, decimal_places=18)

    class Meta:
        indexes = [
            models.Index(fields=["txid"]),
            models.Index(fields=["wallet", "amount"]),
        ]

    def __str__(self):
        """
        Returns a human-readable representation of the transaction,
        including its txid and amount.
        """
        return f"Transaction {self.txid} ({self.amount})"

    def clean(self):
        """
        Validates the transaction before saving.

        - Ensures the transaction is associated with a wallet.
        - Calculates the difference in amount if updating an existing transaction.
        - Checks that the wallet balance after applying this transaction
          will not become negative.

        Raises:
            ValidationError: If wallet is not set or balance constraint is violated.
        """
        if self.wallet_id is None:
            raise ValidationError("Transaction must belong to a wallet.")

        current_balance = self.wallet.balance

        diff = self.amount
        if self.pk:
            try:
                old = Transaction.objects.get(pk=self.pk)
                diff = self.amount - old.amount
            except Transaction.DoesNotExist:
                diff = self.amount
        else:
            diff = self.amount
        new_balance = current_balance + diff
        if new_balance < 0:
            raise ValidationError("Wallet balance cannot become negative.")

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to enforce validation and atomicity.

        - Calls `full_clean` to perform all validations.
        - Wraps the save operation in a database transaction to prevent partial writes.
        """
        self.full_clean()
        with transaction.atomic():
            super().save(*args, **kwargs)

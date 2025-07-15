from decimal import Decimal

from django.db import models
from django.db.models import Sum

from apps.common.exceptions import ValidationError
from apps.common.managers import SoftDeleteManager
from apps.common.mixins import SafeSaveMixin, SoftDeleteMixin, TimestampMixin, UUIDMixin


class Wallet(UUIDMixin, TimestampMixin, SafeSaveMixin, SoftDeleteMixin):
    """
    Represents a Wallet entity that aggregates multiple Transactions.

    Attributes:
      - label: Human-readable name or label for the wallet, indexed for quick search.

    Behavior:
      - Provides a computed `balance` property that sums all related transaction amounts.
      - Validates that the balance is never negative via `update_balance` method.
      - Supports UUID primary key, timestamps, safe saving, and soft deletion via mixins.

    Meta:
      - Adds a database index on the `label` field for efficient querying.
    """

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    label = models.CharField(max_length=255, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["label"]),
        ]

    def __str__(self):
        """
        Returns the wallet's label as its string representation.
        """
        return self.label

    @property
    def balance(self) -> Decimal:
        """
        Computes the current wallet balance as the sum of all related transaction amounts.

        Returns:
            Decimal: The total balance, or 0 if no transactions exist.
        """
        agg = self.transactions.aggregate(total=Sum("amount"))
        return agg["total"] or Decimal("0")

    def update_balance(self):
        """
        Validates that the current balance is not negative.

        Raises:
            ValidationError: If the balance is negative.

        Returns:
            Decimal: The current valid balance.
        """
        balance = self.balance
        if balance < 0:
            raise ValidationError("Wallet balance cannot be negative.")
        return balance

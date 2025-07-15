from decimal import Decimal
from uuid import uuid4

from apps.account.models import Transaction, Wallet


class TransactionService:
    """
    Service class for handling business logic related to Transaction creation
    and validation.

    This centralizes transaction creation to enforce business rules and
    maintain data consistency.
    """

    @classmethod
    def create(cls, wallet: Wallet, amount: Decimal, txid: str = None) -> Transaction:
        """
        Creates and persists a new Transaction linked to the specified wallet,
        generating a unique txid if none is provided.

        Args:
            wallet (Wallet): The Wallet instance to associate with the transaction.
            amount (Decimal): The monetary amount of the transaction (can be positive or negative).
            txid (str, optional): A unique transaction identifier. If omitted, a UUID-based
                hex string will be generated automatically.

        Returns:
            Transaction: The newly created Transaction instance.

        Raises:
            ValidationError: If the transaction violates business constraints such as
                wallet balance becoming negative (handled by model validation).
        """
        tx = Transaction.objects.create(
            wallet=wallet,
            txid=txid or uuid4().hex,
            amount=amount,
        )
        return tx

import logging
from decimal import Decimal
from uuid import uuid4

from apps.account.models import Transaction, Wallet


logger = logging.getLogger(__name__)


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
        generated_txid = txid or uuid4().hex

        logger.info(
            f"Creating transaction: wallet_id={wallet.id}, amount={amount}, txid={generated_txid}"
        )
        logger.debug(f"Wallet before transaction: {wallet.__dict__}")

        tx = Transaction.objects.create(
            wallet=wallet,
            txid=generated_txid,
            amount=amount,
        )

        logger.info(f"Transaction created: id={tx.id}, wallet_id={wallet.id}")
        logger.debug(f"Transaction data: {tx.__dict__}")
        return tx

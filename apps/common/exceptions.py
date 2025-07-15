from rest_framework import status
from rest_framework.exceptions import APIException


class BalanceNegativeError(APIException):
    """
    Exception raised when an operation would cause a wallet's balance to become negative.

    Returns HTTP 400 Bad Request with a descriptive error message.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Wallet balance cannot be negative."
    default_code = "wallet_balance_negative"


class ValidationError(APIException):
    """
    Generic validation error for invalid input or business rule violations.

    Returns HTTP 400 Bad Request with a default validation error message.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Validation error occurred."
    default_code = "validation_error"

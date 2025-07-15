from rest_framework import status
from rest_framework.exceptions import APIException


class TransactionNotFoundError(APIException):
    """
    JSON:API-compliant exception raised when one or more transactions are not found.

    This exception returns HTTP 404 with a descriptive error message
    containing the missing transaction UUIDs.
    """

    status_code = status.HTTP_404_NOT_FOUND
    default_code = "transactions_not_found"

    def __init__(self, missing_ids=None, *args, **kwargs):
        self.missing_ids = missing_ids
        if missing_ids is None:
            detail = kwargs.pop("detail", "Transaction(s) not found.")
        else:
            if isinstance(missing_ids, (str, bytes)):
                missing_ids = [missing_ids]
            detail = {
                "detail": f"Transaction(s) not found: {', '.join(str(_id) for _id in missing_ids)}",
                "missing_ids": missing_ids,
            }
        super().__init__(detail=detail, *args, **kwargs)

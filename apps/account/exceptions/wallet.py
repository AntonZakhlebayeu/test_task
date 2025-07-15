from rest_framework import status
from rest_framework.exceptions import APIException


class WalletNotFoundError(APIException):
    """
    JSON:API-compliant exception raised when one or more wallets are not found.

    This exception is raised from the service layer and returns a 404 response
    with a descriptive error message containing the missing wallet UUIDs.
    """

    status_code = status.HTTP_404_NOT_FOUND
    default_code = "wallets_not_found"

    def __init__(self, missing_ids=None, *args, **kwargs):
        self.missing_ids = missing_ids
        if missing_ids is None:
            detail = kwargs.pop("detail", "Wallet(s) not found.")
        else:
            if isinstance(missing_ids, (str, bytes)):
                missing_ids = [missing_ids]
            detail = {
                "detail": f"Wallet(s) not found: {', '.join(str(_id) for _id in missing_ids)}",
                "missing_ids": missing_ids,
            }

        super().__init__(detail=detail, *args, **kwargs)

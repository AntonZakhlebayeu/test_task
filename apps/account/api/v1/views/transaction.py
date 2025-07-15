import logging

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.filters import OrderingFilter
from rest_framework_json_api.views import ModelViewSet

from apps.account.api.v1.serializers import (
    TransactionRequestSerializer,
    TransactionSerializer,
)
from apps.account.exceptions import TransactionNotFoundError
from apps.account.filters import TransactionFilter
from apps.account.models import Transaction
from apps.common.constants import StandardResultsSetPagination
from apps.common.mixins import (
    APIHandleExceptionMixin,
    AtomicCreateMixin,
    AtomicUpdateMixin,
    CacheResponseMixin,
    SoftDeleteSafeObjectMixin,
)


logger = logging.getLogger(__name__)


class TransactionViewSet(
    SoftDeleteSafeObjectMixin,
    APIHandleExceptionMixin,
    AtomicCreateMixin,
    AtomicUpdateMixin,
    CacheResponseMixin,
    ModelViewSet,
):
    """
    ViewSet for the Transaction model providing standard CRUD operations
    with JSON:API compliance.

    Features:
      - Supports pagination via StandardResultsSetPagination.
      - Supports filtering through DjangoFilterBackend using TransactionFilter.
      - Supports ordering by 'txid', 'amount', and 'created_at' fields.
      - Defaults ordering by descending creation date.
      - Uses atomic database transactions on create and update to ensure consistency.
      - Handles exceptions gracefully with custom API exception handling.

    Queryset:
      - Optimized to select related 'wallet' objects to reduce DB queries.

    Serializer:
      - Uses TransactionSerializer for serialization and validation.
    """

    queryset = Transaction.objects.select_related("wallet").all()
    serializer_class = TransactionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TransactionFilter
    ordering_fields = ["txid", "amount", "created_at"]
    ordering = ["-created_at"]
    not_found_exception_class = TransactionNotFoundError

    def get_cache_timeout(self):
        timeout = None
        if self.action == "list":
            timeout = 40
        elif self.action == "retrieve":
            timeout = 10
        else:
            timeout = super().get_cache_timeout()

        logger.debug(f"Cache timeout for action '{self.action}': {timeout}")
        return timeout

    @extend_schema(
        request=TransactionRequestSerializer,
        responses=TransactionSerializer,
        description="Create a new transaction with JSON:API-compliant body",
    )
    def create(self, request, *args, **kwargs):
        logger.info(f"Creating transaction with data: {request.data}")
        response = super().create(request, *args, **kwargs)
        logger.info(f"Transaction created with response status {response.status_code}")
        return response

    @extend_schema(
        request=TransactionRequestSerializer,
        responses=TransactionSerializer,
        description="Update existing transaction",
    )
    def partial_update(self, request, *args, **kwargs):
        logger.info(f"Partial update of transaction with data: {request.data}")
        response = super().partial_update(request, *args, **kwargs)
        logger.info(f"Transaction updated with response status {response.status_code}")
        return response

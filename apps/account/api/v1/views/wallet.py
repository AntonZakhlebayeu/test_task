from decimal import Decimal

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework_json_api.views import ModelViewSet

from apps.account.api.v1.serializers import (
    DepositRequestSerializer,
    TransactionSerializer,
    TransferRequestSerializer,
    WalletCreateUpdateSerializer,
    WalletSerializer,
)
from apps.account.exceptions import WalletNotFoundError
from apps.account.filters import WalletFilter
from apps.account.models import Wallet
from apps.account.services import WalletService
from apps.common.constants import StandardResultsSetPagination
from apps.common.mixins import (
    APIHandleExceptionMixin,
    AtomicCreateMixin,
    AtomicUpdateMixin,
    CacheResponseMixin,
    SoftDeleteSafeObjectMixin,
)


class WalletViewSet(
    SoftDeleteSafeObjectMixin,
    APIHandleExceptionMixin,
    AtomicCreateMixin,
    AtomicUpdateMixin,
    CacheResponseMixin,
    ModelViewSet,
):
    """
    ViewSet for the Wallet model with JSON:API compliance.

    Features:
      - Supports standard CRUD operations with pagination and filtering.
      - Pagination uses StandardResultsSetPagination.
      - Filtering via DjangoFilterBackend with WalletFilter.
      - Ordering available on 'label', 'created_at', and 'updated_at' fields.
      - Default ordering is by creation date ascending.
      - Atomic transactions on create and update to maintain data integrity.
      - Enhanced exception handling for API responses.

    Custom Actions:
      - deposit: POST to deposit or withdraw funds from a wallet by specifying
        an "amount" (positive or negative) in the request body. Applies the cash flow
        through WalletService and returns status message.
      - transfer: POST to transfer funds between two wallets by specifying
        "source_wallet", "destination_wallet", and "amount" in the request body.
        Uses WalletService.transfer and returns status message.
    """

    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = WalletFilter
    ordering_fields = ["label", "created_at", "updated_at"]
    ordering = ["created_at"]
    not_found_exception_class = WalletNotFoundError

    def get_cache_timeout(self):
        if self.action == "list":
            return 20
        elif self.action == "retrieve":
            return 5
        return super().get_cache_timeout()

    @extend_schema(
        request=WalletCreateUpdateSerializer,
        responses=WalletSerializer,
        description="Create a new wallet with JSON:API-compliant body",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        request=WalletCreateUpdateSerializer,
        responses=WalletSerializer,
        description="Update existing wallet",
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        request=DepositRequestSerializer,
        responses={200: TransactionSerializer},
        description="Deposit or withdraw funds on a specific wallet by amount.",
        methods=["POST"],
        tags=["account"],
    )
    @action(detail=True, methods=["post"])
    def deposit(self, request, pk=None):
        amount = Decimal(request.data.get("amount"))
        transaction = WalletService.apply_cash_flow(wallet_id=pk, amount=amount)
        serializer = TransactionSerializer(
            transaction, context={"message": "Wallet has been deposited"}
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=TransferRequestSerializer,
        responses={200: WalletSerializer(many=True)},
        description="Transfer funds between two wallets atomically.",
        methods=["POST"],
        tags=["account"],
    )
    @action(detail=False, methods=["post"])
    def transfer(self, request):
        source, dest = WalletService.transfer(
            source_id=request.data["source_wallet"],
            dest_id=request.data["destination_wallet"],
            amount=Decimal(request.data["amount"]),
        )
        serializer = WalletSerializer([source, dest], many=True)
        response_data = {
            "data": serializer.data,
            "message": "Transfer has been completed",
        }
        return Response(response_data, status=status.HTTP_200_OK)

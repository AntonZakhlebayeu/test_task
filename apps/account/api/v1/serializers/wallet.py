from rest_framework_json_api import serializers

from apps.account.models import Wallet


class WalletAttributesSerializer(serializers.Serializer):
    """
    Serializer for the attributes of a Wallet JSON:API resource.

    Fields:
      - label: User-defined label or name of the wallet.
    """

    label = serializers.CharField()


class WalletDataSerializer(serializers.Serializer):
    """
    Serializer for the data wrapper of a Wallet JSON:API resource.

    Fields:
      - id: Optional unique identifier of the wallet (string).
      - attributes: WalletAttributesSerializer instance containing wallet fields.
    """

    id = serializers.CharField(required=False)
    attributes = WalletAttributesSerializer()


class WalletCreateUpdateSerializer(serializers.Serializer):
    """
    Serializer for the full JSON:API request body to create or update a Wallet.

    Fields:
      - data: WalletDataSerializer instance wrapping id and attributes.
    """

    data = WalletDataSerializer()


class DepositAttributesSerializer(serializers.Serializer):
    """
    Serializer for the attributes of a Deposit JSON:API resource.

    Fields:
      - amount: Decimal field representing amount to deposit or withdraw,
        supports up to 36 digits and 18 decimal places.
    """

    amount = serializers.DecimalField(max_digits=36, decimal_places=18)


class DepositDataSerializer(serializers.Serializer):
    """
    Serializer for the data wrapper of a Deposit JSON:API resource.

    Fields:
      - attributes: DepositAttributesSerializer instance.
    """

    attributes = DepositAttributesSerializer()


class DepositRequestSerializer(serializers.Serializer):
    """
    Serializer for the full JSON:API request body to deposit or withdraw funds.

    Fields:
      - data: DepositDataSerializer instance wrapping deposit attributes.
    """

    data = DepositDataSerializer()


class TransferAttributesSerializer(serializers.Serializer):
    """
    Serializer for the attributes of a Transfer JSON:API resource.

    Fields:
      - source_wallet: UUID of the source wallet.
      - destination_wallet: UUID of the destination wallet.
      - amount: Decimal amount to transfer with high precision.
    """

    source_wallet = serializers.UUIDField()
    destination_wallet = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=36, decimal_places=18)


class TransferDataSerializer(serializers.Serializer):
    """
    Serializer for the data wrapper of a Transfer JSON:API resource.

    Fields:
      - attributes: TransferAttributesSerializer instance.
    """

    attributes = TransferAttributesSerializer()


class TransferRequestSerializer(serializers.Serializer):
    """
    Serializer for the full JSON:API request body to transfer funds.

    Fields:
      - data: TransferDataSerializer instance wrapping transfer attributes.
    """

    data = TransferDataSerializer()


class WalletSerializer(serializers.ModelSerializer):
    """
    Serializer for the Wallet model compliant with JSON:API specification.

    Fields:
      - id: Read-only unique identifier of the wallet.
      - label: User-defined label/name of the wallet.
      - balance: Read-only decimal field representing the current wallet balance
        with high precision (up to 36 digits, 18 decimal places).

    The `balance` field is marked as read-only and sourced directly from the model's balance attribute.

    JSONAPIMeta:
        Defines the resource name as "wallets" for JSON:API routing.
    """

    balance = serializers.DecimalField(
        max_digits=36,
        decimal_places=18,
        read_only=True,
    )

    class Meta:
        model = Wallet
        fields = ("id", "label", "balance")
        read_only_fields = ("id", "balance")

    class JSONAPIMeta:
        resource_name = "wallets"

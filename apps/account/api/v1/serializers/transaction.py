from rest_framework_json_api import serializers

from apps.account.models import Transaction


class WalletRelationshipSerializer(serializers.Serializer):
    """
    Serializer for the 'wallet' relationship object in JSON:API.

    Fields:
      - data: Dict containing 'type' and 'id' identifying the related wallet resource.
    """

    data = serializers.DictField()


class TransactionAttributesSerializer(serializers.ModelSerializer):
    """
    Serializer for the attributes of a Transaction JSON:API resource,
    excluding relational fields.

    Fields:
      - txid: Unique transaction identifier string.
      - amount: Decimal amount of the transaction with high precision.
    """

    class Meta:
        model = Transaction
        fields = ("txid", "amount")


class TransactionRelationshipsSerializer(serializers.Serializer):
    """
    Serializer for the relationships object in a Transaction JSON:API resource.

    Fields:
      - wallet: WalletRelationshipSerializer instance representing the wallet relationship.
    """

    wallet = WalletRelationshipSerializer()


class TransactionDataSerializer(serializers.Serializer):
    """
    Serializer for the data wrapper of a Transaction JSON:API resource,
    including id, type, attributes, and relationships.

    Fields:
      - id: Optional UUID of the transaction.
      - attributes: TransactionAttributesSerializer instance.
      - relationships: TransactionRelationshipsSerializer instance.
    """

    id = serializers.UUIDField(required=False)
    attributes = TransactionAttributesSerializer()
    relationships = TransactionRelationshipsSerializer()


class TransactionRequestSerializer(serializers.Serializer):
    """
    Wrapper serializer for incoming JSON:API requests for Transaction.

    Fields:
      - data: TransactionDataSerializer instance.

    Validation:
      - Ensures the 'type' field in data is 'transactions'.
    """

    data = TransactionDataSerializer()

    def validate(self, attrs):
        data = attrs.get("data", {})
        if data.get("type") != "transactions":
            raise serializers.ValidationError("Invalid resource type, expected 'transactions'")
        return attrs


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Transaction model compliant with JSON:API specification.

    Fields:
      - id: Read-only unique identifier of the transaction.
      - wallet: Foreign key to the associated wallet.
      - txid: Unique transaction identifier string.
      - amount: Decimal amount of the transaction.

    The serializer enforces read-only behavior for the `id` field.

    JSONAPIMeta:
        Defines the resource name as "transactions" for JSON:API routing.
    """

    message = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ("id", "wallet", "txid", "amount", "message")
        read_only_fields = ("id",)

    class JSONAPIMeta:
        resource_name = "transactions"

    def get_message(self, obj) -> str:
        return self.context.get("message")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if "message" not in self.context:
            data.pop("message", None)
        return data

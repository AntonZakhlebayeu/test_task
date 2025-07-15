from django_filters import rest_framework as filters

from apps.account.models import Transaction


class TransactionFilter(filters.FilterSet):
    """
    FilterSet for the Transaction model enabling filtering based on wallet,
    transaction ID substring matching, and amount range.

    Filters:
      - wallet: Filters transactions by the UUID of the related wallet.
      - txid: Case-insensitive partial match on transaction ID.
      - amount_min: Filters transactions with amount greater than or equal to this value.
      - amount_max: Filters transactions with amount less than or equal to this value.

    Meta:
      Specifies the model and exposed filter fields.
    """

    wallet = filters.UUIDFilter(field_name="wallet__id")
    txid = filters.CharFilter(field_name="txid", lookup_expr="icontains")
    amount_min = filters.NumberFilter(field_name="amount", lookup_expr="gte")
    amount_max = filters.NumberFilter(field_name="amount", lookup_expr="lte")

    class Meta:
        model = Transaction
        fields = ["wallet", "txid", "amount_min", "amount_max"]

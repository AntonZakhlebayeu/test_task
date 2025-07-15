from django_filters import rest_framework as filters

from apps.account.models import Wallet


class WalletFilter(filters.FilterSet):
    """
    FilterSet for the Wallet model allowing filtering by label with case-insensitive
    partial matching.

    Filters:
      - label: Case-insensitive containment search on the wallet label.

    Meta:
      Specifies the model and exposed filter fields.
    """

    label = filters.CharFilter(field_name="label", lookup_expr="icontains")

    class Meta:
        model = Wallet
        fields = ["label"]

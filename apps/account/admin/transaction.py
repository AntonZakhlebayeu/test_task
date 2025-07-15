from django.contrib import admin

from apps.account.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin interface for the Transaction model with optimized query performance.

    - Uses `list_select_related` to prefetch related wallet objects for efficiency.
    - Displays transaction ID, related wallet, transaction ID string, and amount.
    - Allows searching by transaction ID and wallet label.
    - Enables autocomplete for wallet selection to improve usability.
    - Marks creation and update timestamps as read-only.
    """

    list_select_related = ["wallet"]
    list_display = ["id", "wallet", "txid", "amount"]
    search_fields = ["txid", "wallet__label"]
    autocomplete_fields = ["wallet"]
    readonly_fields = ["created_at", "updated_at"]

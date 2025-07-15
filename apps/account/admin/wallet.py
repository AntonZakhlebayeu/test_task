from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.utils.html import format_html

from apps.account.models import Transaction, Wallet


class Last10TransactionFormSet(BaseInlineFormSet):
    """
    Limits the inline formset queryset to show only the last 10 transactions,
    ordered by creation date descending.
    """

    def get_queryset(self):
        qs = super().get_queryset().order_by("-created_at")
        return qs[:10]


class TransactionInline(admin.TabularInline):
    """
    Inline admin interface for Transaction model to be displayed within the Wallet admin page.
    Shows a read-only list of last 10 transactions related to the wallet,
    with change links enabled but deletion disabled.
    """

    model = Transaction
    formset = Last10TransactionFormSet
    extra = 0
    fields = ("id", "txid", "amount", "created_at")
    readonly_fields = fields
    show_change_link = True
    can_delete = False
    verbose_name_plural = "Last 10 Transactions"


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """
    Admin interface for Wallet model.

    Displays wallet details including a colored balance indicator and count of related transactions.
    Includes an inline of the last 10 transactions.
    Read-only fields prevent editing balance and timestamps.
    """

    list_display = ("id", "label", "colored_balance", "transaction_count", "created_at")
    search_fields = ("label",)
    readonly_fields = ("balance", "created_at", "updated_at")
    inlines = [TransactionInline]
    fieldsets = (
        (
            None,
            {
                "fields": ("label",),
            },
        ),
        (
            "Read-only Info",
            {
                "classes": ("collapse",),
                "fields": ("balance", "created_at", "updated_at"),
            },
        ),
    )

    def transaction_count(self, obj):
        """
        Returns the total number of transactions related to this wallet.
        """
        return obj.transactions.count()

    transaction_count.short_description = "Transactions"

    def colored_balance(self, obj):
        """
        Returns the wallet balance wrapped in colored HTML:
        red if the balance is negative, green otherwise.
        """
        color = "red" if obj.balance < 0 else "green"
        return format_html(f'<strong style="color:{color}">{obj.balance}</strong>')

    colored_balance.short_description = "Balance"


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin interface for Transaction model.

    Displays transaction details including associated wallet.
    Read-only fields prevent modifications.
    Disables add/change/delete permissions to enforce creation/modification only via API or Wallet inline.
    """

    list_display = ("id", "txid", "wallet", "amount", "created_at")
    search_fields = ("txid",)
    list_filter = ("wallet",)
    readonly_fields = ("id", "txid", "amount", "wallet", "created_at", "updated_at")

    def has_add_permission(self, request):
        """
        Disable adding transactions directly via the admin interface.
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Disable changing transactions directly via the admin interface.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Disable deleting transactions directly via the admin interface.
        """
        return False

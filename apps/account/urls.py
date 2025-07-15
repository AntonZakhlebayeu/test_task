from rest_framework.routers import DefaultRouter

from apps.account.api.v1.views import TransactionViewSet, WalletViewSet


router = DefaultRouter()
"""
Registers API routes for Wallet and Transaction resources using DRF's DefaultRouter.

Endpoints:
- /wallets/ for WalletViewSet
- /transactions/ for TransactionViewSet

This router automatically generates standard RESTful routes for the registered viewsets.
"""
router.register(r"wallets", WalletViewSet)
router.register(r"transactions", TransactionViewSet)

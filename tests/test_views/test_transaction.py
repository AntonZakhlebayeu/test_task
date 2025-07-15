from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.account.models import Transaction, Wallet


@pytest.mark.django_db
class TestTransactionViewSet:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.wallet = Wallet.objects.create(label="Test Wallet")

    def test_create_transaction(self):
        url = "/api/v1/account/transactions/"
        data = {
            "data": {
                "type": "transactions",
                "attributes": {"txid": "tx123", "amount": "100.00"},
                "relationships": {
                    "wallet": {"data": {"type": "Wallet", "id": str(self.wallet.id)}}
                },
            }
        }

        response = self.client.post(url, data, format="vnd.api+json")
        if response.status_code != status.HTTP_201_CREATED:
            print("Response error data:", response.data)
        assert response.status_code == status.HTTP_201_CREATED

        created = Transaction.objects.get(txid="tx123")
        assert created.amount == Decimal("100.00")
        assert created.wallet == self.wallet

    def test_list_transactions(self):
        Transaction.objects.create(wallet=self.wallet, txid="tx1", amount=Decimal("10"))
        Transaction.objects.create(wallet=self.wallet, txid="tx2", amount=Decimal("20"))

        url = "/api/v1/account/transactions/"
        response = self.client.get(url, format="vnd.api+json")
        if "results" not in response.data:
            print("Response data missing 'results' key:", response.data)
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) == 2

    def test_retrieve_transaction(self):
        tx = Transaction.objects.create(wallet=self.wallet, txid="tx123", amount=Decimal("50"))
        url = f"/api/v1/account/transactions/{tx.id}/"
        response = self.client.get(url, format="vnd.api+json")
        if "id" not in response.data:
            print("Response data missing 'id' key:", response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(tx.id)

    def test_partial_update_transaction(self):
        tx = Transaction.objects.create(wallet=self.wallet, txid="tx123", amount=Decimal("50"))
        url = f"/api/v1/account/transactions/{tx.id}/"
        patch_data = {
            "data": {
                "type": "transactions",
                "id": str(tx.id),
                "attributes": {"amount": "75.00"},
            }
        }
        response = self.client.patch(url, patch_data, format="vnd.api+json")
        if response.status_code != status.HTTP_200_OK:
            print("Patch response error:", response.data)
        assert response.status_code == status.HTTP_200_OK
        tx.refresh_from_db()
        assert tx.amount == Decimal("75.00")

    def test_filter_transactions_by_txid(self):
        Transaction.objects.create(wallet=self.wallet, txid="abc123", amount=Decimal("10"))
        Transaction.objects.create(wallet=self.wallet, txid="def456", amount=Decimal("20"))

        url = "/api/v1/account/transactions/?filter[txid]=abc123"
        response = self.client.get(url, format="vnd.api+json")
        if "results" not in response.data:
            print("Filter response missing 'results' key:", response.data)
        assert response.status_code == status.HTTP_200_OK
        filtered_txs = response.data["results"]
        filtered_txs = [tx for tx in filtered_txs if tx["txid"] == "abc123"]
        assert len(filtered_txs) == 1
        assert filtered_txs[0]["txid"] == "abc123"

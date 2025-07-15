from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.account.models import Wallet


@pytest.mark.django_db
class TestWalletViewSet:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.wallet1 = Wallet.objects.create(label="Wallet 1")
        self.wallet2 = Wallet.objects.create(label="Wallet 2")

    def test_create_wallet(self):
        url = "/api/v1/account/wallets/"
        data = {
            "data": {
                "type": "wallets",
                "attributes": {"label": "New Wallet"},
            }
        }
        response = self.client.post(url, data, format="vnd.api+json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get("label") == "New Wallet"

    def test_list_wallets(self):
        url = "/api/v1/account/wallets/"
        response = self.client.get(url, format="vnd.api+json")
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get("results") or response.data.get("data")
        assert any(w["id"] == str(self.wallet1.id) for w in results)

    def test_retrieve_wallet(self):
        url = f"/api/v1/account/wallets/{self.wallet1.id}/"
        response = self.client.get(url, format="vnd.api+json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(self.wallet1.id)

    def test_partial_update_wallet(self):
        url = f"/api/v1/account/wallets/{self.wallet1.id}/"
        patch_data = {
            "data": {
                "type": "wallets",
                "id": str(self.wallet1.id),
                "attributes": {"label": "Updated Wallet"},
            }
        }
        response = self.client.patch(url, patch_data, format="vnd.api+json")
        assert response.status_code == status.HTTP_200_OK
        self.wallet1.refresh_from_db()
        assert self.wallet1.label == "Updated Wallet"

    def test_deposit_positive_and_negative(self):
        url = f"/api/v1/account/wallets/{self.wallet1.id}/deposit/"
        deposit_data = {
            "data": {
                "type": "wallets",
                "attributes": {"amount": "50.00"},
            }
        }
        response = self.client.post(url, deposit_data, format="vnd.api+json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Wallet has been deposited"

        withdraw_data = {
            "data": {
                "type": "wallets",
                "attributes": {"amount": "-30.00"},
            }
        }
        response = self.client.post(url, withdraw_data, format="vnd.api+json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Wallet has been deposited"

    def test_transfer_between_wallets(self):
        deposit_url = f"/api/v1/account/wallets/{self.wallet1.id}/deposit/"
        deposit_data = {
            "data": {
                "type": "wallets",
                "attributes": {"amount": "100.00"},
            }
        }
        dep_response = self.client.post(deposit_url, deposit_data, format="vnd.api+json")
        assert dep_response.status_code == status.HTTP_200_OK

        url = "/api/v1/account/wallets/transfer/"
        transfer_data = {
            "data": {
                "type": "wallets",
                "attributes": {
                    "source_wallet": str(self.wallet1.id),
                    "destination_wallet": str(self.wallet2.id),
                    "amount": "25.00",
                },
            }
        }
        response = self.client.post(url, transfer_data, format="vnd.api+json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Transfer has been completed"

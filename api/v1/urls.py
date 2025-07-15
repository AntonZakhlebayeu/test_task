from django.urls import include, path

from apps.account.urls import router as account_router


app_name = "api-v1"

urlpatterns = [
    path(
        "v1/healthcheck/",
        include("apps.healthcheck.urls", namespace="app"),
    ),
    path(
        "v1/account/",
        include(account_router.urls),
    ),
]

"""
URL configuration for API version 1.

Routes:
- /v1/healthcheck/  -> Healthcheck app URLs for monitoring API/service health.
- /v1/account/      -> Includes account app's registered routes (wallets, transactions, etc.).

Using namespacing and versioned path prefixes facilitates API versioning and modular URL management.
"""

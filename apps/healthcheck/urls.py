from django.urls import path

from apps.healthcheck.api.v1.views import HealthCheckView


app_name = "healthcheck-v1"

urlpatterns = [
    path("healthz/", HealthCheckView.as_view(), name="healthz"),
]

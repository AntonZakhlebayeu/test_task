from django.urls import include, path


app_name = "api-v1"

urlpatterns = [
    path("v1/healthcheck/", include("apps.healthcheck.urls", namespace="app")),
]

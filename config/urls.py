from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.v1.urls", namespace="api")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        path("api/schema/v1/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/docs/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
    ]

"""
Project-level URL configuration:

- 'admin/': Django admin interface.
- 'api/': Includes versioned API URLs under namespace 'api'.
- Static files served during development with static() helper.

Commented-out section provides OpenAPI schema and Swagger UI integration
for API documentation during development.
"""

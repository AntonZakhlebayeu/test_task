from django.conf import settings
from django.conf.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin


# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.v1.urls", namespace="api")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# if settings.DEBUG:
#     urlpatterns += [
#         path("api/schema/v1/", SpectacularAPIView.as_view(), name="schema"),
#         path(
#             "swagger",
#             SpectacularSwaggerView.as_view(url_name="schema"),
#             name="swagger-ui",
#         ),
#     ]

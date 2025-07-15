import logging
import traceback
import uuid

from django.conf import settings
from django.db import IntegrityError, models, transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import status
from rest_framework.exceptions import APIException, NotFound
from rest_framework_json_api.exceptions import (
    exception_handler as json_api_exception_handler,
)

from apps.common.exceptions import ValidationError
from apps.common.managers import SoftDeleteManager


class AtomicCreateMixin:
    """
    Viewset mixin that wraps the `create()` method in an atomic transaction.

    This ensures that if any part of the object creation fails (e.g., in nested serializers),
    no partial data will be saved to the database.

    Recommended for write endpoints where consistency is critical.
    """

    def create(self, request, *args, **kwargs):
        """
        Perform the create operation within a database transaction.

        :param request: HTTP request
        :return: HTTP response
        """
        with transaction.atomic():
            return super().create(request, *args, **kwargs)


class AtomicUpdateMixin:
    """
    Viewset mixin that wraps the `update()` method in an atomic transaction.

    This prevents data races and ensures safe updates when multiple models or operations are involved.
    """

    def update(self, request, *args, **kwargs):
        """
        Perform the update operation within a database transaction.

        :param request: HTTP request
        :return: HTTP response
        """
        with transaction.atomic():
            return super().update(request, *args, **kwargs)


class UUIDMixin(models.Model):
    """
    Abstract model mixin that replaces the default integer `id` with a UUID.

    This is useful for systems where exposing sequential IDs is discouraged for security or UX reasons.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class SoftDeleteSafeObjectMixin:
    """
    Mixin to prevent access to soft-deleted objects in retrieve/update/delete actions.

    Ensures get_object() returns only non-deleted instances.
    Allows customization of the exception class via `not_found_exception_class`.
    """

    not_found_exception_class = NotFound  # Override in your viewset if needed

    def get_object(self):
        """
        Override DRF's get_object to exclude soft-deleted instances.
        """
        queryset = self.get_queryset().model.all_objects.all()

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        try:
            obj = queryset.get(**filter_kwargs)
        except queryset.model.DoesNotExist:
            raise self.not_found_exception_class(detail=f"{queryset.model.__name__} not found.")

        if getattr(obj, "is_deleted", False):
            raise self.not_found_exception_class(detail=f"{queryset.model.__name__} not found.")

        self.check_object_permissions(self.request, obj)
        return obj


class SoftDeleteMixin(models.Model):
    """
    Abstract model mixin that adds a soft delete mechanism.

    Instead of removing the object from the database, it sets `is_deleted=True`.

    Use this in combination with a custom manager that filters out deleted entries by default.
    """

    is_deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """
        Soft-delete the object by marking it as deleted.
        If already deleted, raise exception to avoid redundant operation.
        """
        if self.is_deleted:
            raise ValidationError("Object is already deleted.")
        self.is_deleted = True
        self.save(using=using)


class TimestampMixin(models.Model):
    """
    Abstract model mixin that adds automatic timestamp fields.

    Fields:
        - created_at: set automatically on creation
        - updated_at: updated automatically on every save
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SafeSaveMixin:
    """
    Mixin for safely saving a model instance inside an atomic block.

    Wraps `save()` in a try/except to catch `IntegrityError` (e.g. for unique constraints),
    and raises a clean DRF validation error instead.
    """

    def safe_save(self, *args, **kwargs):
        """
        Save the instance in a transaction-safe way, converting integrity issues to API errors.

        :raises ValidationError: if integrity violation occurs
        :return: the result of `save()`
        """
        try:
            with transaction.atomic():
                return self.save(*args, **kwargs)
        except IntegrityError:
            raise ValidationError("Data conflict or duplicate entry.")


logger = logging.getLogger(__name__)


class APIHandleExceptionMixin:
    """
    ViewSet mixin to improve exception handling and ensure consistent JSON:API error formatting.

    - Automatically logs full tracebacks in DEBUG mode.
    - Converts known custom exceptions into DRF-compatible ones.
    - Supports returning proper HTTP status codes for common errors.
    - Delegates to JSON:API exception handler for proper serialization.
    """

    def handle_exception(self, exc):
        """
        Centralized exception handler with optional traceback printing and custom mapping.

        :param exc: The original exception
        :return: A Response object returned by DRF's JSON:API exception handler
        """
        if settings.DEBUG:
            traceback.print_exc()

        logger.warning("API Exception: %s", str(exc), exc_info=settings.DEBUG)

        if isinstance(exc, Exception) and not isinstance(exc, APIException):
            # Fallback to 500 for unhandled exceptions
            exc = APIException(detail="Internal server error.")

        response = json_api_exception_handler(exc, self.get_exception_handler_context())

        if response is None:
            response = self._default_fallback_response()

        return response

    def _default_fallback_response(self):
        """
        Generates a default 500 Internal Server Error response.

        :return: DRF JSON:API-compliant Response
        """
        from rest_framework.response import Response

        return Response(
            {
                "errors": [
                    {
                        "status": str(status.HTTP_500_INTERNAL_SERVER_ERROR),
                        "title": "Internal Server Error",
                        "detail": "An unexpected error occurred.",
                    }
                ]
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class CacheResponseMixin:
    """
    Mixin to cache the responses of GET requests for ViewSets.

    Applies caching to the `list` and `retrieve` actions by wrapping them with
    Django's `cache_page` decorator.

    The cache timeout duration can be customized per ViewSet by overriding
    the `cache_timeout` attribute or by implementing the `get_cache_timeout` method.

    Usage:
        - Set `cache_timeout` as an integer number of seconds.
        - Or override `get_cache_timeout(self)` to compute timeout dynamically.

    Example:
        class MyViewSet(CacheResponseMixin, ModelViewSet):
            cache_timeout = 120  # cache for 2 minutes

        or

        class MyViewSet(CacheResponseMixin, ModelViewSet):
            def get_cache_timeout(self):
                # Return custom timeout depending on request or other logic
                return 300

    Notes:
        - This mixin caches only the GET methods `list` and `retrieve`.
        - Cache keys are generated automatically based on request path and query params.
        - Be sure to invalidate or clear cache appropriately when data changes.
    """

    cache_timeout = 60  # default cache timeout in seconds

    def get_cache_timeout(self):
        """
        Returns the timeout duration for the cache in seconds.

        Override this method to customize cache duration dynamically.

        :return: int - timeout in seconds
        """
        return self.cache_timeout

    @method_decorator(cache_page(lambda self: self.get_cache_timeout()))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(lambda self: self.get_cache_timeout()))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

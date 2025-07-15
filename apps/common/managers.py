from django.db import models


class SoftDeleteManager(models.Manager):
    """
    Manager to filter out soft-deleted objects by default.
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

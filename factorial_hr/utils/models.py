import uuid
from django.db import models
from django.db.models import Q
from simple_history.models import HistoricalRecords
from django.utils import timezone
from typing import Optional
from django.conf import settings

class UUIDBasedModel(models.Model):
    uuid = models.CharField(max_length=36, default=uuid.uuid4, editable=False, unique=True)
    is_active = models.BooleanField(default=True)
    id = models.BigAutoField(unique=True, primary_key=True)

    class Meta:
        abstract = True


class HistoricalModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    changes_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_modified",
    )

    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(HistoricalModel, self).save(*args, **kwargs)
        if self.changes_by:
            self.history.create(
                history_date=self.updated_at,
                history_change_reason=None,
                history_user=self.changes_by,
                created_at=timezone.now(),
                history_type=self.get_history_type(),
                id=self.id,
            )

    def get_history_type(self):
        """
        Método para determinar el tipo de cambio en el registro histórico.
        Retorna '+' si es una creación, '~' si es una modificación, o '-' si es una eliminación.
        """
        if self.deleted_at:
            return "-"
        elif self._state.adding:
            return "+"
        else:
            return "~"


class MaintainerBaseModel(UUIDBasedModel, models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        super().save()

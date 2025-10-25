# factorial_hr/apps/auth/models.py
from django.db import models
import uuid
from datetime import timedelta
from django.utils import timezone
from factorial_hr.utils.models import UUIDBasedModel, HistoricalModel

def default_expiry():
    return timezone.now() + timedelta(days=7)

class RefreshToken(UUIDBasedModel, HistoricalModel):
    key = models.CharField(max_length=128, unique=True, default=uuid.uuid4)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='refresh_tokens')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiry)
    revoked = models.BooleanField(default=False)

    class Meta:
        app_label = "authentication"

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def revoke(self):
        self.revoked = True
        self.save()
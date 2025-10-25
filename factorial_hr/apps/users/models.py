from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from factorial_hr.utils.models import UUIDBasedModel, HistoricalModel
from factorial_hr.apps.users.utils.user_manager import UserManager

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin, UUIDBasedModel, HistoricalModel):
    code = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    family_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    document_number = models.CharField(max_length=12, blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=12, unique=True, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)

    # Explicit fields needed for Django admin and user checks
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = "users"

        permissions = (
            ('bulk_upload_user', 'can create user in bulk'),
        )

    objects = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    @property
    def user_full_name(self):
        formatted_user_name = list()
        if self.name:
            formatted_user_name.append(self.name)
        if self.family_name:
            formatted_user_name.append(self.family_name)
        if self.last_name:
            formatted_user_name.append(self.last_name)
        return " ".join(formatted_user_name)

    def __str__(self):
        name = self.name if self.name else ""
        email = self.email if self.email else ""
        phone_number = self.phone_number if self.phone_number else ""

        return f"{name} {email} {phone_number}"
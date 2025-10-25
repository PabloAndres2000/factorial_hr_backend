
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
     path("api/", include(("factorial_hr.apps.api.urls", "api"), namespace="api")),
]

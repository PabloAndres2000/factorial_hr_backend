from rest_framework import routers

from factorial_hr.apps.auth.api.view import AuthViewSet

router = routers.SimpleRouter()


router.register(r"authentications", AuthViewSet, basename="authentications")



urlpatterns = router.urls

from rest_framework.routers import DefaultRouter

from .views import AirplaneViewSet


router = DefaultRouter()

router.register(
    'airplanes',
    AirplaneViewSet,
    basename='airplane'
)

urlpatterns = router.urls
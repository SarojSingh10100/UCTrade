from rest_framework.routers import DefaultRouter
from .views import VideoViewSet
from django.urls import path, include

router = DefaultRouter()
router.register('', VideoViewSet, basename='videos')

urlpatterns = [
    path('', include(router.urls)),
]

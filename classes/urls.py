from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ClassSessionViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register(r'', ClassSessionViewSet, basename='classes')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollments')

urlpatterns = [
    path('', include(router.urls)),
]
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CourseEnrollmentViewSet, CourseViewSet, PDFMaterialViewSet

router = DefaultRouter()
router.register(r'', CourseViewSet, basename='courses')
router.register(r'materials', PDFMaterialViewSet, basename='materials')
router.register(r'enrollments', CourseEnrollmentViewSet, basename='enrollments')

urlpatterns = [
    path('', include(router.urls)),
]

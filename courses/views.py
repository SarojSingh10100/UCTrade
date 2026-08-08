from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Course, CourseEnrollment, PDFMaterial
from .permissions import IsCourseOwner, IsInstructor
from .serializers import CourseEnrollmentSerializer, CourseSerializer, PDFMaterialSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('-created_at')
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsInstructor()]
        if self.action in {'update', 'partial_update', 'destroy', 'enrolled_users'}:
            return [IsInstructor(), IsCourseOwner()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, pk=None):
        course = self.get_object()
        if course.price > 0:
            return Response(
                {'detail': 'This is a paid course. Complete payment before enrollment.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        enrollment, created = CourseEnrollment.objects.get_or_create(user=request.user, course=course)
        if created:
            return Response({'detail': 'Enrolled successfully.'}, status=status.HTTP_201_CREATED)
        return Response({'detail': 'Already enrolled.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def enrolled_users(self, request, pk=None):
        course = self.get_object()
        users = course.enrollments.values_list('user__username', flat=True)
        return Response({'users': list(users)})


class PDFMaterialViewSet(viewsets.ModelViewSet):
    queryset = PDFMaterial.objects.all().order_by('-uploaded_at')
    serializer_class = PDFMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in {'create', 'update', 'partial_update', 'destroy'}:
            return [IsInstructor()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not user.is_instructor:
            queryset = queryset.filter(course__enrollments__user=user)
        else:
            queryset = queryset.filter(course__instructor=user)
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset


class CourseEnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CourseEnrollment.objects.all().order_by('-enrolled_at')
    serializer_class = CourseEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_instructor:
            queryset = queryset.filter(course__instructor=user)
        else:
            queryset = queryset.filter(user=user)
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset

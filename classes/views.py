from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ClassSession, Enrollment
from .serializers import ClassSessionSerializer, EnrollmentSerializer


class ClassSessionViewSet(viewsets.ModelViewSet):
    queryset = ClassSession.objects.all().order_by('-created_at')
    serializer_class = ClassSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, pk=None):
        session = self.get_object()
        enrollment, created = Enrollment.objects.get_or_create(user=request.user, class_session=session)
        if created:
            return Response({'detail': 'Enrolled successfully.'}, status=status.HTTP_201_CREATED)
        return Response({'detail': 'Already enrolled.'}, status=status.HTTP_200_OK)


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Enrollment.objects.all().order_by('-enrolled_at')
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
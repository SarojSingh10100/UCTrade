from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from ..models import Video
from ..serializers import VideoSerializer


class VideoAccessPermission(permissions.BasePermission):
    """
    Custom permission to control video access based on enrollment and trial status
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only instructors can create/modify videos
        return request.user and request.user.is_authenticated and request.user.is_instructor

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            # Check access based on video settings
            if obj.access_level == 'public':
                return True
            elif obj.access_level == 'enrolled':
                # Check if user is enrolled in the course
                return (request.user and request.user.is_authenticated and
                       obj.course.enrollments.filter(user=request.user).exists())
            elif obj.access_level == 'premium':
                # Check if user has premium access (you can extend this logic)
                return (request.user and request.user.is_authenticated and
                       hasattr(request.user, 'is_premium') and request.user.is_premium)
        # For non-safe methods, only uploader can modify
        return obj.uploaded_by == request.user


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = (VideoAccessPermission,)

    def get_queryset(self):
        queryset = Video.objects.all()
        course_id = self.request.query_params.get('course', None)
        is_trial = self.request.query_params.get('trial', None)

        if course_id:
            queryset = queryset.filter(course_id=course_id)

        if is_trial:
            queryset = queryset.filter(is_trial=True)

        return queryset

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    @action(detail=True, methods=['get'])
    def stream(self, request, pk=None):
        """
        Stream video with access control and trial limitations
        """
        try:
            video = self.get_object()

            # Check access permissions
            if not self.check_object_permissions(request, video):
                return Response(
                    {'error': 'Access denied. Please enroll in the course to view this video.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # For trial videos, implement time-based access
            if video.is_trial:
                # You can implement session-based trial tracking here
                # For now, just allow access but log it
                pass

            # Return video URL or stream info
            if video.file:
                video_url = request.build_absolute_uri(video.file.url)
            elif video.url:
                video_url = video.url
            else:
                return Response(
                    {'error': 'Video file not available'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response({
                'video_url': video_url,
                'is_trial': video.is_trial,
                'trial_duration': video.trial_duration if video.is_trial else None,
                'access_level': video.access_level
            })

        except Video.DoesNotExist:
            return Response(
                {'error': 'Video not found'},
                status=status.HTTP_404_NOT_FOUND
            )

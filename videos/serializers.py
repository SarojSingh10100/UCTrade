from rest_framework import serializers
from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.ReadOnlyField(source='uploaded_by.username')
    course_title = serializers.ReadOnlyField(source='course.title')

    class Meta:
        model = Video
        fields = ('id', 'course', 'course_title', 'title', 'file', 'url', 'uploaded_by',
                 'created_at', 'is_trial', 'trial_duration', 'access_level')
        read_only_fields = ('uploaded_by', 'created_at')

    def validate(self, attrs):
        course = attrs.get('course', getattr(self.instance, 'course', None))
        request = self.context.get('request')
        if request and course and course.instructor_id != request.user.id:
            raise serializers.ValidationError({'course': 'You can only manage lectures for your own courses.'})
        has_video = attrs.get('file') or attrs.get('url') or getattr(self.instance, 'file', None) or getattr(self.instance, 'url', None)
        if not has_video:
            raise serializers.ValidationError('Provide a video file or URL.')
        return attrs

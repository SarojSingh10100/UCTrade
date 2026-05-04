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

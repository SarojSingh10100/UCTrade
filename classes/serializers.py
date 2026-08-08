from rest_framework import serializers

from .models import ClassSession, Enrollment


class ClassSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSession
        fields = ('id', 'course', 'title', 'description', 'start_time', 'end_time', 'capacity', 'created_at')
        read_only_fields = ('created_at',)

    def validate(self, attrs):
        start_time = attrs.get('start_time', getattr(self.instance, 'start_time', None))
        end_time = attrs.get('end_time', getattr(self.instance, 'end_time', None))
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({'end_time': 'End time must be after start time.'})
        course = attrs.get('course', getattr(self.instance, 'course', None))
        request = self.context.get('request')
        if request and course and course.instructor_id != request.user.id:
            raise serializers.ValidationError({'course': 'You can only schedule classes for your own courses.'})
        return attrs


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ('id', 'user', 'class_session', 'enrolled_at', 'notified')
        read_only_fields = ('user', 'enrolled_at', 'notified')

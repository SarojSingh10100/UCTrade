from rest_framework import serializers

from .models import Course, CourseEnrollment, PDFMaterial


class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.ReadOnlyField(source='instructor.username')

    class Meta:
        model = Course
        fields = ('id', 'title', 'slug', 'description', 'price', 'instructor', 'created_at')
        read_only_fields = ('slug', 'created_at', 'instructor')


class PDFMaterialSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.ReadOnlyField(source='uploaded_by.username')

    class Meta:
        model = PDFMaterial
        fields = ('id', 'course', 'file', 'title', 'uploaded_by', 'uploaded_at')
        read_only_fields = ('uploaded_by', 'uploaded_at')

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            user = request.user
            if not getattr(user, 'is_instructor', False) and validated_data.get('course').instructor_id != user.id:
                raise serializers.ValidationError('Only instructors or course owners can upload materials')
            validated_data['uploaded_by'] = user
        return super().create(validated_data)


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseEnrollment
        fields = ('id', 'user', 'course', 'enrolled_at')
        read_only_fields = ('user', 'enrolled_at')

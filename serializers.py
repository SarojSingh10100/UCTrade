from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import (
    User, Cart, CartItem, ClassSession, Enrollment, Course, PDFMaterial,
    CourseEnrollment, Notification, Order, OrderItem, Transaction, Video
)

User = get_user_model()


# Users App Serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_instructor')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'is_instructor')

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({"password": "Passwords must match."})
        validate_password(attrs.get('password'))
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# Cart App Serializers
class CartItemSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_price = serializers.DecimalField(source='course.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'course', 'course_title', 'course_price', 'quantity')


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'total_amount', 'created_at')
        read_only_fields = ('user', 'created_at', 'total_amount')

    def get_total_amount(self, obj):
        return sum(item.course.price * item.quantity for item in obj.items.all())


# Classes App Serializers
class ClassSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSession
        fields = ('id', 'course', 'title', 'description', 'start_time', 'end_time', 'capacity')


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ('id', 'user', 'class_session', 'enrolled_at')
        read_only_fields = ('enrolled_at',)


# Courses App Serializers
class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.ReadOnlyField(source='instructor.username')

    class Meta:
        model = Course
        fields = ('id', 'title', 'slug', 'description', 'price', 'instructor', 'created_at')
        read_only_fields = ('slug', 'created_at')


class PDFMaterialSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.ReadOnlyField(source='uploaded_by.username')

    class Meta:
        model = PDFMaterial
        fields = ('id', 'course', 'file', 'title', 'uploaded_by', 'uploaded_at')
        read_only_fields = ('uploaded_by', 'uploaded_at')

    def create(self, validated_data):
        # Ensure uploader is instructor and optionally course owner
        request = self.context.get('request')
        if request and request.user:
            user = request.user
            if not user.is_instructor and user != validated_data.get('course').instructor:
                raise serializers.ValidationError('Only instructors can upload materials')
            validated_data['uploaded_by'] = user
        return super().create(validated_data)


# Notifications App Serializers
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'title', 'message', 'read', 'created_at')
        read_only_fields = ('created_at',)


# Payments App Serializers
class OrderItemSerializer(serializers.ModelSerializer):
    course_detail = CourseSerializer(source='course', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'course', 'course_detail', 'quantity', 'price')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'total_amount', 'paid', 'created_at', 'items')
        read_only_fields = ('user', 'created_at', 'paid')


class CreateOrderSerializer(serializers.Serializer):
    # expects items: [{course: id, quantity: 1}]
    items = serializers.ListField(child=serializers.DictField())

    def validate(self, attrs):
        # basic validation
        if not attrs.get('items'):
            raise serializers.ValidationError('No items provided')
        return attrs


# Videos App Serializers
class VideoSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.ReadOnlyField(source='uploaded_by.username')
    course_title = serializers.ReadOnlyField(source='course.title')

    class Meta:
        model = Video
        fields = ('id', 'course', 'course_title', 'title', 'file', 'url', 'uploaded_by',
                 'created_at', 'is_trial', 'trial_duration', 'access_level')
        read_only_fields = ('uploaded_by', 'created_at')
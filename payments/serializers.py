from rest_framework import serializers
from .models import Order, OrderItem, Transaction
from courses.serializers import CourseSerializer


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

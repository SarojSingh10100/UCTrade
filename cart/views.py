from decimal import Decimal

from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from .models import Cart, CartItem
from .serializers import CartSerializer
from courses.models import Course
from payments.models import Order, OrderItem as PaymentOrderItem


class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def create(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        course_id = request.data.get('course')
        if not course_id:
            return Response({'detail': 'course is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        if course.price <= 0:
            return Response({'detail': 'Free courses can be enrolled in directly.'}, status=status.HTTP_400_BAD_REQUEST)
        if course.instructor_id == request.user.id:
            return Response({'detail': 'You cannot purchase your own course.'}, status=status.HTTP_400_BAD_REQUEST)

        item, created = CartItem.objects.get_or_create(cart=cart, course=course, defaults={'quantity': 1})
        if not created:
            item.quantity += 1
            item.save()
        return Response({'id': item.id, 'course': course.id}, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        try:
            item = cart.items.get(pk=pk)
        except CartItem.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def checkout(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        if not cart.items.exists():
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = Decimal('0.00')
        for item in cart.items.select_related('course').all():
            total_amount += item.course.price * item.quantity

        order = Order.objects.create(user=request.user, total_amount=total_amount, paid=False)
        for item in cart.items.select_related('course').all():
            PaymentOrderItem.objects.create(
                order=order,
                course=item.course,
                quantity=item.quantity,
                price=item.course.price,
            )

        cart.items.all().delete()
        return Response({'order_id': order.id, 'total_amount': str(order.total_amount)}, status=status.HTTP_201_CREATED)

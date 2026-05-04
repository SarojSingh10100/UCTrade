import stripe
import json
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, permissions, generics, status, response
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    User, Cart, CartItem, ClassSession, Enrollment, Course, PDFMaterial,
    CourseEnrollment, Notification, Order, OrderItem, Transaction, Video
)
from .serializers import (
    UserSerializer, RegisterSerializer, CartSerializer, CartItemSerializer,
    ClassSessionSerializer, EnrollmentSerializer, CourseSerializer, PDFMaterialSerializer,
    NotificationSerializer, OrderSerializer, OrderItemSerializer, CreateOrderSerializer,
    VideoSerializer
)

User = get_user_model()
logger = logging.getLogger(__name__)
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)


# Users App Views
class RegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


# Cart App Views
class CartViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def create(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.validated_data['course']
        quantity = serializer.validated_data.get('quantity', 1)
        item, created = CartItem.objects.get_or_create(cart=cart, course=course, defaults={'quantity': quantity})
        if not created:
            item.quantity = quantity
            item.save()
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item = get_object_or_404(CartItem, pk=pk, cart=cart)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def checkout(self, request):
        # Create an Order from the user's cart
        cart, _ = Cart.objects.get_or_create(user=request.user)
        if cart.items.count() == 0:
            return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        # calculate total and create order
        total = 0
        order = None
        for item in cart.items.all():
            total += float(item.course.price) * item.quantity
        order = Order.objects.create(user=request.user, total_amount=total)
        for item in cart.items.all():
            OrderItem.objects.create(order=order, course=item.course, quantity=item.quantity, price=item.course.price)

        return Response({'order_id': order.id}, status=status.HTTP_201_CREATED)


# Classes App Views
class ClassSessionViewSet(viewsets.ModelViewSet):
    queryset = ClassSession.objects.all()
    serializer_class = ClassSessionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, pk=None):
        cls = self.get_object()
        user = request.user
        enrollment, created = Enrollment.objects.get_or_create(user=user, class_session=cls)
        if not created:
            return Response({'detail': 'Already enrolled'}, status=status.HTTP_400_BAD_REQUEST)

        # schedule notification (background task)
        try:
            from notifications.tasks import send_notification
            title = f"Enrolled: {cls.title}"
            message = f"You have been enrolled in {cls.title} starting at {cls.start_time}."
            send_notification.delay(user.id, title, message)
        except Exception:
            pass

        return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED)


# Courses App Views
class IsInstructorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Everyone can list/retrieve, only instructors can create
        if view.action in ['list', 'retrieve']:
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_instructor

    def has_object_permission(self, request, view, obj):
        # Read-only allowed for any
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only owner instructor can edit/delete
        return obj.instructor == request.user


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (IsInstructorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)


class PDFMaterialViewSet(viewsets.ModelViewSet):
    queryset = PDFMaterial.objects.all()
    serializer_class = PDFMaterialSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        qs = super().get_queryset().order_by('-uploaded_at')
        course_id = self.request.query_params.get('course')
        if course_id:
            qs = qs.filter(course_id=course_id)
        return qs

    def perform_create(self, serializer):
        # enforce only instructors or course owner
        user = self.request.user
        course = serializer.validated_data.get('course')
        if not user.is_authenticated:
            raise permissions.PermissionDenied('Authentication required')
        if not user.is_instructor and course.instructor != user:
            raise permissions.PermissionDenied('Only instructors or course owners can upload')
        serializer.save(uploaded_by=user)


# Notifications App Views
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save()


# Payments App Views
class CreatePaymentIntentView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        order_id = request.data.get('order_id')
        try:
            order = Order.objects.get(pk=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)

        try:
            # If Stripe secret is not configured and we're in DEBUG, simulate a PaymentIntent for local testing
            if not stripe.api_key and getattr(settings, 'DEBUG', False):
                intent = {'id': f'test_pi_{order.id}', 'client_secret': f'test_cs_{order.id}'}
            else:
                if not stripe.api_key:
                    return Response({'detail': 'Stripe not configured.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                intent = stripe.PaymentIntent.create(
                    amount=int(order.total_amount * 100),
                    currency='usd',
                    metadata={'order_id': str(order.id)}
                )

            # Create pending transaction
            txn = Transaction.objects.create(order=order, provider_payment_id=intent['id'] if isinstance(intent, dict) else intent.id, amount=order.total_amount, status='pending')
            return Response({'client_secret': intent['client_secret'] if isinstance(intent, dict) else intent.client_secret})
        except Exception as exc:
            logger.exception('Failed to create payment intent')
            # also print to stdout so test runner captures the exception details
            print('CreatePaymentIntentView exception:', repr(exc))
            import traceback
            traceback.print_exc()
            return Response({'detail': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StripeWebhookView(APIView):
    # webhook should be configured without auth
    permission_classes = ()

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
        try:
            if endpoint_secret:
                event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            else:
                # fallback when webhook signing secret is not configured in env
                try:
                    event = stripe.Event.construct_from(request.data, stripe.api_key)
                except Exception:
                    event = request.data
        except Exception as e:
            logger.exception('Failed to parse Stripe webhook')
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # handle the payment_intent.succeeded
        if event['type'] == 'payment_intent.succeeded':
            intent = event['data']['object']
            pid = intent['id']
            # mark transaction/order as paid
            try:
                txn = Transaction.objects.get(provider_payment_id=pid)
                txn.status = 'succeeded'
                txn.save()
                order = txn.order
                order.paid = True
                order.save()
                # enroll the user and notify via celery
                try:
                    from notifications.tasks import send_enrollment_notifications_for_order
                    send_enrollment_notifications_for_order.delay(order.id)
                except Exception:
                    # fallback to synchronous call if celery not available
                    try:
                        from notifications.tasks import send_enrollment_notifications_for_order
                        send_enrollment_notifications_for_order(order.id)
                    except Exception:
                        pass
            except Transaction.DoesNotExist:
                pass

        return Response(status=status.HTTP_200_OK)


# Videos App Views
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
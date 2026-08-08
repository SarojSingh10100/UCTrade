import stripe
import json
import logging
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Order, Transaction
from courses.models import CourseEnrollment

logger = logging.getLogger(__name__)
# set stripe key from settings (safe default if not present)
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)


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
            # If Stripe secret is not configured, simulate a PaymentIntent for local testing.
            if not stripe.api_key:
                intent = {'id': f'test_pi_{order.id}', 'client_secret': f'test_cs_{order.id}'}
            else:
                intent = stripe.PaymentIntent.create(
                    amount=int(order.total_amount * 100),
                    currency='usd',
                    metadata={'order_id': str(order.id)}
                )

            # Create pending transaction
            txn = Transaction.objects.create(order=order, provider_payment_id=intent['id'] if isinstance(intent, dict) else intent.id, amount=order.total_amount, status='pending')
            return Response({'client_secret': intent['client_secret'] if isinstance(intent, dict) else intent.client_secret}, status=status.HTTP_200_OK)
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

                for item in order.items.all():
                    CourseEnrollment.objects.get_or_create(user=order.user, course=item.course)

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

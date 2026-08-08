from django.urls import path
from payments.views.payment import CreatePaymentIntentView, StripeWebhookView

urlpatterns = [
    path('create-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
]

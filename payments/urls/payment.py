from django.urls import path
from ..views.payment import CreatePaymentIntentView, OrderHistoryView, StripeWebhookView

urlpatterns = [
    path('create-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('orders/', OrderHistoryView.as_view(), name='payment-history'),
]

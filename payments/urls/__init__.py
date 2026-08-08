from django.urls import path, include

from payments.urls.payment import urlpatterns as payment_urlpatterns

urlpatterns = payment_urlpatterns

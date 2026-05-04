from django.urls import path, include

urlpatterns = [
    path('', include('payments.urls.payment')),
]

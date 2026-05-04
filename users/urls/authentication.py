from django.urls import path
from ..views import RegistrationView, ProfileView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('me/', ProfileView.as_view(), name='profile'),
]

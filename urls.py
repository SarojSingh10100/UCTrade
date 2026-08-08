from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import all URLs from apps
urlpatterns = [
    # Users URLs
    path('users/', include('users.urls')),

    # Cart URLs
    path('cart/', include('cart.urls')),

    # Classes URLs
    path('classes/', include('classes.urls')),

    # Courses URLs
    path('courses/', include('courses.urls')),

    # Notifications URLs
    path('notifications/', include('notifications.urls')),

    # Payments URLs
    path('payments/', include('payments.urls')),

    # Videos URLs
    path('videos/', include('videos.urls')),

    # Trade URLs
    path('trade/', include('trade.urls')),
# ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


    # Classes URLs
    path('classes/', include(classes_router.urls)),

    # Courses URLs
    path('courses/', include(courses_router.urls)),

    # Notifications URLs
    path('notifications/', include(notifications_router.urls)),

    # Payments URLs
    path('payments/create-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('payments/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),

    # Videos URLs
    path('videos/', include(videos_router.urls)),
]

# Add static files serving for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


##from uctrade.urls import urlpatterns
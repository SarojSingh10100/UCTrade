from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from .models import Notification

User = get_user_model()


@shared_task
def send_notification(user_id, title, message, send_email=True):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return False

    Notification.objects.create(user=user, title=title, message=message)
    if send_email and user.email:
        # Use Django email backend configured in settings
        send_mail(subject=title, message=message, from_email=None, recipient_list=[user.email], fail_silently=False)
    return True

def send_enrollment_notifications_for_order(order_id):
    """Helper to notify and enroll users to courses in an order."""
    try:
        from payments.models import Order
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return False

    for item in order.items.all():
        course = item.course
        # enroll user in course
        from courses.models import CourseEnrollment
        CourseEnrollment.objects.get_or_create(user=order.user, course=course)
        # notify user
        title = f"You are enrolled: {course.title}"
        message = f"Congratulations! You have access to {course.title}."
        send_notification.delay(order.user.id, title, message, send_email=True)
    return True

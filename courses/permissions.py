from rest_framework.permissions import BasePermission


class IsInstructor(BasePermission):
    message = 'Instructor access is required.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_instructor)


class IsCourseOwner(BasePermission):
    message = 'You do not have permission to modify this course.'

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_authenticated and obj.instructor_id == request.user.id)

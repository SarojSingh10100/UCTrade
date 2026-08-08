from django.contrib import admin

from .models import ClassSession, Enrollment


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'start_time', 'end_time', 'capacity')
    search_fields = ('title', 'course__title')
    list_filter = ('start_time', 'end_time')
    ordering = ('-start_time',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'class_session', 'enrolled_at', 'notified')
    search_fields = ('user__username', 'class_session__title')
    list_filter = ('notified',)
    ordering = ('-enrolled_at',)

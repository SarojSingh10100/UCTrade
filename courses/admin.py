from django.contrib import admin

from .models import Course, CourseEnrollment, PDFMaterial


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'price', 'created_at')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(PDFMaterial)
class PDFMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'uploaded_by', 'uploaded_at')


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at')

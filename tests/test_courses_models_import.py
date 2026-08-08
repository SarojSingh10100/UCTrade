from django.test import SimpleTestCase

from courses.models import Course, CourseEnrollment, PDFMaterial


class CoursesModelsImportTests(SimpleTestCase):
    def test_courses_models_are_importable(self):
        self.assertEqual(Course._meta.app_label, 'courses')
        self.assertEqual(CourseEnrollment._meta.app_label, 'courses')
        self.assertEqual(PDFMaterial._meta.app_label, 'courses')

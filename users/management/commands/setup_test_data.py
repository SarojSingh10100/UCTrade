from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Course, PDFMaterial, CourseEnrollment
from videos.models import Video
from classes.models import ClassSession
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up test data for the UCTRADE LMS platform'

    def handle(self, *args, **options):
        self.stdout.write('Setting up test data...')

        # Create test users
        self.create_test_users()

        # Create test courses
        self.create_test_courses()

        # Create test videos
        self.create_test_videos()

        # Create test classes
        self.create_test_classes()

        # Create enrollments
        self.create_enrollments()

        self.stdout.write(
            self.style.SUCCESS('Test data setup complete!')
        )
        self.stdout.write('\nTest User Credentials:')
        self.stdout.write('Admin: admin@example.com / admin123')
        self.stdout.write('Student: student@example.com / student123')
        self.stdout.write('Instructor: instructor@example.com / instructor123')
        self.stdout.write('\nFree Trial User: trial@example.com / trial123 (can access all trial videos)')

    def create_test_users(self):
        """Create test users with different roles"""
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@example.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
                'is_instructor': True
            },
            {
                'username': 'instructor',
                'email': 'instructor@example.com',
                'password': 'instructor123',
                'first_name': 'John',
                'last_name': 'Instructor',
                'is_instructor': True
            },
            {
                'username': 'student',
                'email': 'student@example.com',
                'password': 'student123',
                'first_name': 'Jane',
                'last_name': 'Student',
                'is_instructor': False
            },
            {
                'username': 'trial',
                'email': 'trial@example.com',
                'password': 'trial123',
                'first_name': 'Trial',
                'last_name': 'User',
                'is_instructor': False
            }
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults=user_data
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f'Created user: {user.email}')
            else:
                self.stdout.write(f'User already exists: {user.email}')

    def create_test_courses(self):
        """Create test courses"""
        instructor = User.objects.get(email='instructor@example.com')

        courses_data = [
            {
                'title': 'Python for Beginners',
                'slug': 'python-beginners',
                'description': 'Learn Python programming from scratch with hands-on projects.',
                'price': 49.99,
                'instructor': instructor
            },
            {
                'title': 'Web Development with React',
                'slug': 'react-web-development',
                'description': 'Build modern web applications using React and modern JavaScript.',
                'price': 79.99,
                'instructor': instructor
            },
            {
                'title': 'Data Science Fundamentals',
                'slug': 'data-science-fundamentals',
                'description': 'Introduction to data analysis, statistics, and machine learning basics.',
                'price': 99.99,
                'instructor': instructor
            },
            {
                'title': 'Free Trial Course',
                'slug': 'free-trial-course',
                'description': 'Try our platform with this free course featuring trial videos.',
                'price': 0.00,
                'instructor': instructor
            }
        ]

        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                slug=course_data['slug'],
                defaults=course_data
            )
            if created:
                self.stdout.write(f'Created course: {course.title}')
            else:
                self.stdout.write(f'Course already exists: {course.title}')

    def create_test_videos(self):
        """Create test videos for courses"""
        courses = Course.objects.all()

        for course in courses:
            # Create trial videos for each course
            trial_video_data = {
                'course': course,
                'title': f'{course.title} - Introduction (Trial)',
                'url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
                'uploaded_by': course.instructor,
                'is_trial': True,
                'trial_duration': 300,  # 5 minutes
                'access_level': 'public'
            }

            trial_video, created = Video.objects.get_or_create(
                title=trial_video_data['title'],
                course=course,
                defaults=trial_video_data
            )

            if created:
                self.stdout.write(f'Created trial video: {trial_video.title}')

            # Create full access videos (only for paid courses)
            if course.price > 0:
                full_video_data = {
                    'course': course,
                    'title': f'{course.title} - Full Lesson 1',
                    'url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4',
                    'uploaded_by': course.instructor,
                    'is_trial': False,
                    'access_level': 'enrolled'
                }

                full_video, created = Video.objects.get_or_create(
                    title=full_video_data['title'],
                    course=course,
                    defaults=full_video_data
                )

                if created:
                    self.stdout.write(f'Created full video: {full_video.title}')

    def create_test_classes(self):
        """Create test live classes"""
        instructor = User.objects.get(email='instructor@example.com')
        courses = Course.objects.filter(price__gt=0)

        from datetime import datetime, timedelta
        import pytz

        tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(tz)

        for i, course in enumerate(courses):
            class_data = {
                'title': f'{course.title} - Live Session {i+1}',
                'description': f'Live interactive session for {course.title}',
                'course': course,
                'start_time': now + timedelta(days=i+1, hours=2),
                'end_time': now + timedelta(days=i+1, hours=3),
                'capacity': 50
            }

            live_class, created = ClassSession.objects.get_or_create(
                title=class_data['title'],
                defaults=class_data
            )

            if created:
                self.stdout.write(f'Created live class: {live_class.title}')

    def create_enrollments(self):
        """Create test enrollments"""
        student = User.objects.get(email='student@example.com')
        courses = Course.objects.filter(price__gt=0)

        for course in courses:
            enrollment, created = CourseEnrollment.objects.get_or_create(
                user=student,
                course=course
            )
            if created:
                self.stdout.write(f'Enrolled {student.email} in {course.title}')
            else:
                self.stdout.write(f'{student.email} already enrolled in {course.title}')
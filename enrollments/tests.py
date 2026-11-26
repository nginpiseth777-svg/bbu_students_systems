from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date

from students.models import Student
from courses.models import Course
from .models import Enrollment


class EnrollmentListTests(TestCase):
    def test_enrollment_page_requires_login(self):
        response = self.client.get(reverse('enrollments:enrollment_list'))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_enrollment_page_lists_enrollments(self):
        user = User.objects.create_user(username='enrollment-student')
        student = Student.objects.create(
            user=user,
            student_id='BBU-ENROLL-001',
            date_of_birth=date(2000, 1, 1),
            gender='O',
            address='Phnom Penh',
            city='Phnom Penh',
        )
        instructor = User.objects.create_user(username='enrollment-instructor')
        course = Course.objects.create(
            code='IT-101',
            title='Web Development',
            description='Web development course',
            instructor=instructor,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 1),
        )
        Enrollment.objects.create(
            student=student,
            course=course,
            status='ENROLLED',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('enrollments:enrollment_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'enrollments/enrollment_list.html')
        self.assertContains(response, 'BBU-ENROLL-001')
        self.assertContains(response, 'IT-101')

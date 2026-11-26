from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date

from .models import Course


class LecturerCampusFilterTests(TestCase):
    def test_siem_reap_filter_lists_only_siem_reap_lecturers(self):
        siem_user = User.objects.create_user(
            username='siem-lecturer',
            first_name='Siem',
            last_name='Lecturer',
        )
        phnom_user = User.objects.create_user(
            username='phnom-lecturer',
            first_name='Phnom',
            last_name='Lecturer',
        )
        course_data = {
            'description': 'Course',
            'credits': 3,
            'start_date': date(2026, 1, 1),
            'end_date': date(2026, 6, 1),
        }
        Course.objects.create(
            code='SR-101',
            title='Siem Reap Course',
            instructor=siem_user,
            campus='SIEM_REAP',
            **course_data,
        )
        Course.objects.create(
            code='PN-101',
            title='Phnom Penh Course',
            instructor=phnom_user,
            campus='PHNOM_PENH',
            **course_data,
        )

        response = self.client.get(
            reverse('courses:lecturer_list'),
            {'campus': 'SIEM_REAP'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'សៀមរាប')
        self.assertContains(response, 'Siem Lecturer')
        self.assertNotContains(response, 'Phnom Lecturer')

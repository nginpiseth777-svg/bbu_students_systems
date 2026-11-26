from datetime import date
from decimal import Decimal
from io import BytesIO
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .forms import StudentRegistrationForm
from .models import Student


class StudentDashboardTests(TestCase):
    def test_login_and_logout_links_work_for_guests_and_users(self):
        user = User.objects.create_user(
            username='login-student',
            password='StrongPass123!',
        )

        guest_response = self.client.get(reverse('login'))
        self.assertEqual(guest_response.status_code, 200)
        self.assertContains(guest_response, 'action="/accounts/login/"')
        self.assertContains(guest_response, 'name="next"')

        login_response = self.client.post(
            reverse('login'),
            {
                'username': 'login-student',
                'password': 'StrongPass123!',
                'next': reverse('students:student_list'),
            },
        )
        self.assertRedirects(login_response, reverse('students:student_list'))

        authenticated_response = self.client.get(reverse('home'))
        self.assertContains(authenticated_response, 'login-student')
        self.assertContains(authenticated_response, 'action="/accounts/logout/"')

        logout_response = self.client.post(reverse('logout'))
        self.assertEqual(logout_response.status_code, 302)
        self.assertEqual(logout_response.url, reverse('home'))

    def test_registration_page_renders_styled_form(self):
        response = self.client.get(reverse('students:register'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'registration-page')
        self.assertContains(response, 'registration-submit')
        self.assertContains(response, 'site-footer')
        self.assertContains(response, 'href="/courses/"')
        self.assertContains(response, 'href="/courses/lecturers/"')
        self.assertContains(response, 'href="#about-us"')
        self.assertContains(response, 'data-theme-toggle')
        self.assertContains(response, 'src="/static/js/site-theme.js?v=20261121-ambient-motion"')
        self.assertContains(
            response,
            'https://www.google.com/maps/search/?api=1&amp;query=Build+Bright+University+Cambodia',
        )
        self.assertContains(response, 'facebook.com/search/top')
        self.assertContains(response, 'youtube.com/results')
        self.assertContains(response, 'instagram.com/explore/search')

    def test_registration_creates_user_and_student_profile(self):
        response = self.client.post(
            reverse('students:register'),
            {
                'username': 'new-student',
                'password1': 'SafePassword123!xyz',
                'password2': 'SafePassword123!xyz',
                'first_name': 'New',
                'last_name': 'Student',
                'email': 'new-student@example.com',
                'student_id': 'BBU-NEW-001',
                'khmer_name': 'និស្សិតថ្មី',
                'date_of_birth': '2000-01-01',
                'gender': 'O',
                'phone_number': '',
                'address': 'Phnom Penh',
                'city': 'Phnom Penh',
                'country': 'Cambodia',
            },
        )

        user = User.objects.get(username='new-student')
        student = Student.objects.get(user=user)
        self.assertRedirects(
            response,
            reverse('students:student_detail', kwargs={'pk': student.pk}),
        )
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'Student')
        self.assertEqual(user.email, 'new-student@example.com')

    def test_registration_rejects_an_existing_student_id(self):
        user = User.objects.create_user(username='existing-student')
        Student.objects.create(
            user=user,
            student_id='BBU-EXIST-001',
            date_of_birth=date(2000, 1, 1),
            gender='O',
            address='Phnom Penh',
            city='Phnom Penh',
        )
        form = StudentRegistrationForm(data={'student_id': 'BBU-EXIST-001'})

        self.assertFalse(form.is_valid())
        self.assertIn('student_id', form.errors)

    def test_legacy_unprotected_student_update_route_is_not_available(self):
        response = self.client.get('/students/students/1/update/')

        self.assertEqual(response.status_code, 404)

    def test_lecturer_directory_page_renders(self):
        response = self.client.get(reverse('courses:lecturer_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'សាស្ត្រាចារ្យ')

    def test_student_profile_update_page_renders_both_forms(self):
        user = User.objects.create_user(username='profile-edit-student')
        student = Student.objects.create(
            user=user,
            student_id='BBU-EDIT-001',
            date_of_birth=date(2000, 1, 1),
            gender='O',
            address='Phnom Penh',
            city='Phnom Penh',
        )
        self.client.force_login(user)

        response = self.client.get(
            reverse('students:student_update', kwargs={'pk': student.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'profile-edit-page')
        self.assertContains(response, 'name="student_id"')
        self.assertContains(response, 'name="gpa"')
        self.assertContains(response, 'min="0"')
        self.assertContains(response, 'max="4"')
        self.assertContains(response, 'step="0.01"')
        self.assertContains(response, 'name="is_active"')
        self.assertContains(response, 'កំពុងសិក្សា')
        self.assertContains(response, 'មិនបានសិក្សា')
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'profile-save-button')
        self.assertContains(response, 'data-profile-photo-preview')
        self.assertContains(response, 'student-profile-preview.js')

    def test_uploaded_profile_picture_is_saved_and_shown_in_student_list(self):
        user = User.objects.create_user(username='picture-student')
        student = Student.objects.create(
            user=user,
            student_id='BBU-PICTURE-001',
            date_of_birth=date(2000, 1, 1),
            gender='O',
            address='Phnom Penh',
            city='Phnom Penh',
        )
        self.client.force_login(user)
        image_buffer = BytesIO()
        Image.new('RGB', (1, 1), color='blue').save(image_buffer, format='PNG')
        image_bytes = image_buffer.getvalue()

        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(DEBUG=True, MEDIA_ROOT=media_root):
                response = self.client.post(
                    reverse('students:student_update', kwargs={'pk': student.pk}),
                    {
                        'student_id': student.student_id,
                        'khmer_name': 'និស្សិតសាកល្បង',
                        'gpa': '3.25',
                        'is_active': 'False',
                        'date_of_birth': '2000-01-01',
                        'gender': 'O',
                        'address': 'Phnom Penh',
                        'city': 'Phnom Penh',
                        'country': 'Cambodia',
                        'username': user.username,
                        'first_name': '',
                        'last_name': '',
                        'email': '',
                        'profile_picture': SimpleUploadedFile(
                            'student.png', image_bytes, content_type='image/png'
                        ),
                    },
                )

                self.assertEqual(response.status_code, 302)
                self.assertRedirects(
                    response,
                    reverse('students:student_detail', kwargs={'pk': student.pk}),
                )
                student.refresh_from_db()
                self.assertTrue(student.profile_picture)
                self.assertEqual(student.gpa, Decimal('3.25'))
                self.assertFalse(student.is_active)
                self.assertTrue(
                    student.profile_picture.storage.exists(student.profile_picture.name)
                )

                list_response = self.client.get(reverse('students:student_list'))
                self.assertContains(list_response, student.profile_picture.url)
                self.assertContains(list_response, 'មិនបានសិក្សា')

    def test_dashboard_shows_accurate_stats_when_searching(self):
        active_user = User.objects.create_user(username='active-student')
        inactive_user = User.objects.create_user(username='inactive-student')
        common_details = {
            'date_of_birth': date(2000, 1, 1),
            'gender': 'O',
            'address': 'Phnom Penh',
            'city': 'Phnom Penh',
        }
        Student.objects.create(
            user=active_user,
            student_id='BBU-001',
            gpa=Decimal('3.00'),
            **common_details,
        )
        Student.objects.create(
            user=inactive_user,
            student_id='BBU-002',
            gpa=Decimal('4.00'),
            is_active=False,
            **common_details,
        )

        self.client.force_login(active_user)
        response = self.client.get(
            reverse('students:student_list'),
            {'q': 'BBU-001'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/static/css/style.css?v=20261121-profile-picture-preview"')
        self.assertContains(response, 'src="/static/js/dashboard.js?v=20261121-dashboard"')
        self.assertContains(
            response,
            'src="/static/js/student-search.js?v=20261126-name-suggestions"',
        )
        self.assertContains(response, 'dashboard-glow')
        self.assertEqual(response.context['student_stats']['total'], 2)
        self.assertEqual(response.context['student_stats']['active'], 1)
        self.assertEqual(response.context['student_stats']['average_gpa'], Decimal('3.5'))
        self.assertEqual(response.context['students'].paginator.count, 1)

    def test_search_matches_full_english_and_khmer_names(self):
        matching_user = User.objects.create_user(
            username='sophea-sok',
            first_name='Sophea',
            last_name='Sok',
        )
        other_user = User.objects.create_user(
            username='sophea-chan',
            first_name='Sophea',
            last_name='Chan',
        )
        common_details = {
            'date_of_birth': date(2000, 1, 1),
            'gender': 'O',
            'address': 'Phnom Penh',
            'city': 'Phnom Penh',
        }
        Student.objects.create(
            user=matching_user,
            student_id='BBU-SEARCH-001',
            khmer_name='សុខ សុភា',
            **common_details,
        )
        Student.objects.create(
            user=other_user,
            student_id='BBU-SEARCH-002',
            khmer_name='ចាន់ សុភា',
            **common_details,
        )
        self.client.force_login(matching_user)

        for query in ('Sophea Sok', 'សុខ សុភា'):
            with self.subTest(query=query):
                response = self.client.get(
                    reverse('students:student_list'),
                    {'q': query},
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context['students'].paginator.count, 1)
                self.assertContains(response, 'BBU-SEARCH-001')
                self.assertNotContains(response, 'BBU-SEARCH-002')

    def test_student_name_suggestions_are_limited_to_matching_names(self):
        matching_user = User.objects.create_user(
            username='suggestion-sophea',
            first_name='Sophea',
            last_name='Sok',
        )
        other_user = User.objects.create_user(username='suggestion-other')
        common_details = {
            'date_of_birth': date(2000, 1, 1),
            'gender': 'O',
            'address': 'Phnom Penh',
            'city': 'Phnom Penh',
        }
        matching_student = Student.objects.create(
            user=matching_user,
            student_id='BBU-SUGGEST-001',
            khmer_name='សុខ សុភា',
            **common_details,
        )
        Student.objects.create(
            user=other_user,
            student_id='BBU-SUGGEST-002',
            khmer_name='ចាន់ វិសាល',
            **common_details,
        )
        endpoint = reverse('students:student_suggestions')

        guest_response = self.client.get(endpoint, {'q': 'Sophea'})
        self.assertEqual(guest_response.status_code, 302)

        self.client.force_login(matching_user)
        response = self.client.get(endpoint, {'q': 'Sophea Sok'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'results': [
                    {
                        'name': 'សុខ សុភា',
                        'url': reverse(
                            'students:student_detail',
                            kwargs={'pk': matching_student.pk},
                        ),
                    }
                ]
            },
        )

        short_query_response = self.client.get(endpoint, {'q': 'S'})
        self.assertEqual(short_query_response.json(), {'results': []})
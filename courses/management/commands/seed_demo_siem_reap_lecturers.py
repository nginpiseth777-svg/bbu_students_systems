from datetime import date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Course


DEMO_LECTURERS = [
    {
        'username': 'demo-siem-reap-sopheak',
        'first_name': 'DEMO - សុភ័ក្រ',
        'last_name': 'សៀមរាប',
        'email': 'demo-sopheak@example.invalid',
        'code': 'IT-SR-101',
        'title': 'DEMO: Introduction to Information Technology',
    },
    {
        'username': 'demo-siem-reap-dara',
        'first_name': 'DEMO - ដារ៉ា',
        'last_name': 'សៀមរាប',
        'email': 'demo-dara@example.invalid',
        'code': 'MG-SR-201',
        'title': 'DEMO: Business Management',
    },
    {
        'username': 'demo-siem-reap-maly',
        'first_name': 'DEMO - ម៉ាលី',
        'last_name': 'សៀមរាប',
        'email': 'demo-maly@example.invalid',
        'code': 'EN-SR-101',
        'title': 'DEMO: English for Academic Purposes',
    },
]


class Command(BaseCommand):
    help = 'Seed clearly labeled demo lecturers for the Siem Reap campus.'

    def handle(self, *args, **options):
        created_users = 0
        created_courses = 0

        with transaction.atomic():
            for lecturer in DEMO_LECTURERS:
                user, user_created = User.objects.update_or_create(
                    username=lecturer['username'],
                    defaults={
                        'first_name': lecturer['first_name'],
                        'last_name': lecturer['last_name'],
                        'email': lecturer['email'],
                    },
                )
                if user_created:
                    user.set_unusable_password()
                    user.save(update_fields=['password'])

                _, course_created = Course.objects.update_or_create(
                    code=lecturer['code'],
                    defaults={
                        'title': lecturer['title'],
                        'description': 'ព្រឹត្តិការណ៍សាកល្បងសម្រាប់បង្ហាញ UI។ មិនមែនទិន្នន័យសាស្ត្រាចារ្យផ្លូវការ។',
                        'instructor': user,
                        'credits': 3,
                        'level': '100',
                        'capacity': 40,
                        'status': 'ACTIVE',
                        'campus': 'SIEM_REAP',
                        'start_date': date(2026, 1, 1),
                        'end_date': date(2026, 6, 30),
                    },
                )
                created_users += int(user_created)
                created_courses += int(course_created)

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {created_users} demo users and {created_courses} demo courses '
            'for Siem Reap.'
        ))

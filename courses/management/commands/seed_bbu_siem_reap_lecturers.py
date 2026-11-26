from datetime import date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from courses.models import Course


LECTURERS = [
    ('Chhai', 'Lihov', 7, 29),
    ('Mon', 'Minh', 21, 19),
    ('Chan', 'Thavrak', 6, 11),
    ('Prum', 'Sopheanoch', 25, 10),
    ('Siem', 'Royal', 28, 2),
    ('Chan', 'Bunrath', 5, 0),
    ('Chhang', 'Seha', 8, 0),
    ('Chhoem', 'Hay', 9, 0),
    ('Kao', 'Luy Peou', 10, 0),
    ('Khoeurt', 'Sopha', 11, 0),
    ('Kim', 'Chanrong', 12, 0),
    ('Kim', 'Sovanndy', 13, 0),
    ('Kol', 'Sereyrith', 14, 0),
    ('Lay', 'Chanveasna', 15, 0),
    ('Lor', 'Soth', 16, 0),
]


class Command(BaseCommand):
    help = 'Seed 15 lecturers published on the BBU SR IT showcase directory.'

    def handle(self, *args, **options):
        with transaction.atomic():
            demo_usernames = User.objects.filter(
                username__startswith='demo-siem-reap-'
            )
            Course.objects.filter(
                Q(code__startswith='MG-SR-')
                | Q(code__startswith='EN-SR-')
                | Q(code__startswith='IT-SR-')
            ).delete()
            demo_usernames.delete()

            created_users = 0
            created_courses = 0

            for index, (first_name, last_name, profile_id, capstone_count) in enumerate(
                LECTURERS, start=1
            ):
                username = f'bbu-sr-lecturer-{profile_id}'
                user, user_created = User.objects.update_or_create(
                    username=username,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': f'{username}@bbusrithub.site',
                    },
                )
                if user_created:
                    user.set_unusable_password()
                    user.save(update_fields=['password'])

                course_code = f'BBU-SR-L{index:02d}'
                _, course_created = Course.objects.update_or_create(
                    code=course_code,
                    defaults={
                        'title': f'Senior IT Lecturer - {first_name} {last_name}',
                        'description': (
                            'Lecturer at the Faculty of Science and Technology, '
                            'Build Bright University (Siem Reap IT Showcase). '
                            f'{capstone_count} supervised capstones. '
                            f'Source: https://bbusrithub.site/lecturers/{profile_id}'
                        ),
                        'instructor': user,
                        'credits': 0,
                        'level': '100',
                        'capacity': 40,
                        'status': 'ACTIVE',
                        'campus': 'SIEM_REAP',
                        'start_date': date(2026, 1, 1),
                        'end_date': date(2026, 12, 31),
                    },
                )
                created_users += int(user_created)
                created_courses += int(course_created)

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {len(LECTURERS)} BBU Siem Reap lecturers '
            f'({created_users} new users, {created_courses} new course records).'
        ))

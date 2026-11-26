import csv
from datetime import date
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.models import Course


class Command(BaseCommand):
    help = 'Import verified Siem Reap lecturer and course data from CSV.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        csv_path = Path(options['csv_file'])
        if not csv_path.is_file():
            raise CommandError(f'CSV file not found: {csv_path}')

        required = [
            'username', 'first_name', 'last_name', 'email',
            'course_code', 'course_title', 'description',
            'credits', 'level', 'capacity', 'status',
            'start_date', 'end_date',
        ]
        created_users = 0
        created_courses = 0

        with csv_path.open('r', encoding='utf-8-sig', newline='') as source:
            reader = csv.DictReader(source)
            missing = [field for field in required if field not in (reader.fieldnames or [])]
            if missing:
                raise CommandError(
                    'Missing required CSV columns: ' + ', '.join(missing)
                )

            with transaction.atomic():
                for row_number, row in enumerate(reader, start=2):
                    username = (row['username'] or '').strip()
                    course_code = (row['course_code'] or '').strip()
                    if not username or not course_code:
                        raise CommandError(
                            f'Row {row_number}: username and course_code are required.'
                        )

                    user, user_created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'first_name': row['first_name'].strip(),
                            'last_name': row['last_name'].strip(),
                            'email': row['email'].strip(),
                        },
                    )
                    if not user_created:
                        user.first_name = row['first_name'].strip()
                        user.last_name = row['last_name'].strip()
                        user.email = row['email'].strip()
                        user.save(update_fields=['first_name', 'last_name', 'email'])
                    else:
                        user.set_unusable_password()
                        user.save(update_fields=['password'])

                    try:
                        start_date = date.fromisoformat(row['start_date'].strip())
                        end_date = date.fromisoformat(row['end_date'].strip())
                        credits = int(row['credits'])
                        capacity = int(row['capacity'])
                    except (TypeError, ValueError) as exc:
                        raise CommandError(
                            f'Row {row_number}: invalid date or numeric value.'
                        ) from exc

                    course, course_created = Course.objects.update_or_create(
                        code=course_code,
                        defaults={
                            'title': row['course_title'].strip(),
                            'description': row['description'].strip(),
                            'instructor': user,
                            'credits': credits,
                            'level': row['level'].strip() or '100',
                            'capacity': capacity,
                            'status': row['status'].strip() or 'ACTIVE',
                            'campus': 'SIEM_REAP',
                            'start_date': start_date,
                            'end_date': end_date,
                        },
                    )
                    created_users += int(user_created)
                    created_courses += int(course_created)

        self.stdout.write(self.style.SUCCESS(
            f'Imported Siem Reap lecturers: '
            f'{created_users} new users, {created_courses} new courses.'
        ))

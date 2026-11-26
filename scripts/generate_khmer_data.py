import os
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_system.settings')

import django

django.setup()

from django.contrib.auth.models import User
from django.db import transaction

from students.models import Student


COUNT = 200
STUDENT_ID_PREFIX = 'BBUDEMO2026'
USERNAME_PREFIX = 'demo_bbu_2026'

KHMER_GIVEN_NAMES = [
    'ដារ៉ា', 'សុភា', 'វិសាល', 'មាលា', 'ចន្ទ្រា',
    'សុវណ្ណ', 'កញ្ញា', 'បញ្ញា', 'រតនា', 'ស្រីពៅ',
    'វណ្ណៈ', 'ធារ៉ា', 'មុនី', 'សុជាតា', 'កុសល',
    'សំណាង', 'ពិសិដ្ឋ', 'លក្ខិណា', 'សុភ័ក្រ', 'វីរៈ',
]
KHMER_FAMILY_NAMES = [
    'សុខ', 'ជា', 'គង់', 'ហេង', 'លី',
    'ចាន់', 'មាស', 'ពេជ្រ', 'ឡុង', 'អ៊ុំ',
]
ENGLISH_GIVEN_NAMES = [
    'Dara', 'Sophea', 'Visal', 'Maly', 'Chantra',
    'Sovann', 'Kanha', 'Panha', 'Rathana', 'Srey Pov',
    'Vannak', 'Theara', 'Mony', 'Socheata', 'Kosal',
    'Samnang', 'Piseth', 'Leakena', 'Sopheak', 'Vireak',
]
ENGLISH_FAMILY_NAMES = [
    'Sok', 'Chea', 'Kong', 'Heng', 'Ly',
    'Chan', 'Meas', 'Pich', 'Long', 'Oum',
]
CITIES = [
    'ភ្នំពេញ', 'សៀមរាប', 'បាត់ដំបង', 'កំពង់ចាម', 'កំពត',
    'កណ្តាល', 'តាកែវ', 'ព្រះសីហនុ', 'កំពង់ធំ', 'បន្ទាយមានជ័យ',
]


def build_student_data(index):
    given_index = (index - 1) % len(KHMER_GIVEN_NAMES)
    family_index = (index - 1) // len(KHMER_GIVEN_NAMES)
    english_given_index = (index - 1) % len(ENGLISH_GIVEN_NAMES)
    english_family_index = (index - 1) // len(ENGLISH_GIVEN_NAMES)

    return {
        'student_id': f'{STUDENT_ID_PREFIX}{index:03d}',
        'khmer_name': (
            f'{KHMER_FAMILY_NAMES[family_index]} '
            f'{KHMER_GIVEN_NAMES[given_index]}'
        ),
        'first_name': ENGLISH_GIVEN_NAMES[english_given_index],
        'last_name': ENGLISH_FAMILY_NAMES[english_family_index],
        'date_of_birth': date(1998 + index % 9, index % 12 + 1, index % 27 + 1),
        'gender': ('M', 'F', 'O')[index % 3],
        'city': CITIES[index % len(CITIES)],
        'gpa': Decimal((index * 37) % 401) / Decimal('100'),
        'is_active': index % 10 != 0,
    }


def main():
    created = 0
    with transaction.atomic():
        for index in range(1, COUNT + 1):
            data = build_student_data(index)
            if Student.objects.filter(student_id=data['student_id']).exists():
                continue

            username = f'{USERNAME_PREFIX}_{index:04d}'
            if User.objects.filter(username=username).exists():
                raise RuntimeError(
                    f'Username {username} exists without its demo student record.'
                )

            user = User.objects.create_user(
                username=username,
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=f'{username}@example.invalid',
                password=None,
            )
            Student.objects.create(
                user=user,
                student_id=data['student_id'],
                khmer_name=data['khmer_name'],
                date_of_birth=data['date_of_birth'],
                gender=data['gender'],
                phone_number=None,
                address=f'ផ្ទះលេខ {index}, ផ្លូវគំរូ',
                city=data['city'],
                country='Cambodia',
                gpa=data['gpa'],
                is_active=data['is_active'],
            )
            created += 1

    print(f'Created {created} demo students; total students: {Student.objects.count()}.')


if __name__ == '__main__':
    main()
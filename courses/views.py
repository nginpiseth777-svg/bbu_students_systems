from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count
from .models import Course


def course_list(request):
    courses = Course.objects.select_related('instructor').all()
    return render(request, 'courses/course_list.html', {'courses': courses})


def lecturer_list(request):
    campus = request.GET.get('campus', 'SIEM_REAP')
    lecturers = (
        User.objects.filter(
            courses_taught__isnull=False,
            courses_taught__campus=campus,
        )
        .annotate(course_count=Count('courses_taught', distinct=True))
        .prefetch_related('courses_taught')
        .order_by('first_name', 'last_name', 'username')
    )
    campus_labels = dict(Course.CAMPUS_CHOICES)
    contains_demo_data = lecturers.filter(
        first_name__startswith='DEMO',
    ).exists()
    return render(request, 'courses/lecturer_list.html', {
        'lecturers': lecturers,
        'campus': campus,
        'campus_label': campus_labels.get(campus, campus),
        'campus_choices': Course.CAMPUS_CHOICES,
        'contains_demo_data': contains_demo_data,
    })
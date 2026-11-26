from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q

from .models import Enrollment


@login_required
def enrollment_list(request):
    enrollments = (
        Enrollment.objects.select_related('student__user', 'course')
        .all()
        .order_by('-enrollment_date', 'course__code')
    )
    stats = Enrollment.objects.aggregate(
        total=Count('pk'),
        active=Count('pk', filter=Q(status='ENROLLED')),
        completed=Count('pk', filter=Q(status='COMPLETED')),
    )

    return render(request, 'enrollments/enrollment_list.html', {
        'enrollments': enrollments,
        'enrollment_stats': stats,
    })
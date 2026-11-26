from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET

from .forms import StudentForm, StudentRegistrationForm, UserForm
from .models import Student


def _search_students(search_query):
    students = Student.objects.select_related('user').all()
    for search_term in search_query.split():
        students = students.filter(
            Q(student_id__icontains=search_term)
            | Q(khmer_name__icontains=search_term)
            | Q(user__first_name__icontains=search_term)
            | Q(user__last_name__icontains=search_term)
            | Q(user__username__icontains=search_term)
        )
    return students


@login_required
def student_list(request):
    search_query = request.GET.get('q', '').strip()
    students = _search_students(search_query)
    student_stats = Student.objects.aggregate(
        total=Count('pk'),
        active=Count('pk', filter=Q(is_active=True)),
        average_gpa=Avg('gpa'),
    )

    page_obj = Paginator(students.order_by('student_id'), 20).get_page(
        request.GET.get('page')
    )
    return render(
        request,
        'students/student_list.html',
        {
            'students': page_obj,
            'page_obj': page_obj,
            'search_query': search_query,
            'student_stats': student_stats,
        },
    )


@login_required
@require_GET
def student_suggestions(request):
    search_query = request.GET.get('q', '').strip()
    if len(search_query) < 2:
        return JsonResponse({'results': []})

    students = _search_students(search_query).order_by('student_id')[:8]
    return JsonResponse({
        'results': [
            {
                'name': student.get_primary_name(),
                'url': student.get_absolute_url(),
            }
            for student in students
        ],
    })


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    enrollments = student.enrollments.select_related('course').all()
    return render(
        request,
        'students/student_detail.html',
        {'student': student, 'enrollments': enrollments},
    )


@login_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student_form = StudentForm(
            request.POST,
            request.FILES,
            instance=student,
        )
        user_form = UserForm(request.POST, instance=student.user)
        if student_form.is_valid() and user_form.is_valid():
            student_form.save()
            user_form.save()
            messages.success(
                request,
                f"បានកែប្រែទិន្នន័យ {student.student_id} ដោយជោគជ័យ!",
            )
            return redirect('students:student_detail', pk=student.pk)
    else:
        student_form = StudentForm(instance=student)
        user_form = UserForm(instance=student.user)

    return render(
        request,
        'students/student_form.html',
        {
            'student_form': student_form,
            'user_form': user_form,
            'student': student,
        },
    )


def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.email = form.cleaned_data['email']
                user.save()
                student = Student.objects.create(
                    user=user,
                    student_id=form.cleaned_data['student_id'],
                    khmer_name=form.cleaned_data.get('khmer_name', ''),
                    date_of_birth=form.cleaned_data['date_of_birth'],
                    gender=form.cleaned_data['gender'],
                    phone_number=form.cleaned_data.get('phone_number', ''),
                    address=form.cleaned_data['address'],
                    city=form.cleaned_data['city'],
                    country=form.cleaned_data['country'],
                )
            messages.success(request, 'ការចុះឈ្មោះបានជោគជ័យ!')
            login(request, user)
            return redirect('students:student_detail', pk=student.pk)
    else:
        form = StudentRegistrationForm()

    return render(request, 'students/register.html', {'form': form})

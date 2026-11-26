from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Student


class StudentForm(forms.ModelForm):
    """Form for editing a student's profile."""

    is_active = forms.TypedChoiceField(
        choices=[
            ('True', 'កំពុងសិក្សា'),
            ('False', 'មិនបានសិក្សា'),
        ],
        coerce=lambda value: value == 'True',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='ស្ថានភាពសិក្សា',
    )

    class Meta:
        model = Student
        fields = [
            'student_id',
            'khmer_name',
            'gpa',
            'is_active',
            'date_of_birth',
            'gender',
            'phone_number',
            'address',
            'city',
            'country',
            'profile_picture',
        ]
        widgets = {
            'student_id': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'BBU2026001'}
            ),
            'khmer_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'ឈ្មោះជាភាសាខ្មែរ',
                }
            ),
            'gpa': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                    'max': '4',
                    'step': '0.01',
                }
            ),
            'date_of_birth': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(
                attrs={'class': 'form-control', 'accept': 'image/*'}
            ),
        }
        labels = {'gpa': 'GPA (0–4)'}


class UserForm(forms.ModelForm):
    """Form for editing a user's account details."""

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class StudentRegistrationForm(UserCreationForm):
    """Registration form for a user account and student profile."""

    khmer_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    student_id = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'BBU2026001'}
        ),
    )
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={'class': 'form-control', 'type': 'date'}
        ),
    )
    gender = forms.ChoiceField(
        choices=Student.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )
    city = forms.CharField(
        initial='Phnom Penh',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    country = forms.CharField(
        initial='Cambodia',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    def clean_student_id(self):
        student_id = self.cleaned_data['student_id']
        if Student.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError('This student ID is already registered.')
        return student_id

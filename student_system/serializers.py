from rest_framework import serializers
from students.models import Student
from courses.models import Course
from enrollments.models import Enrollment

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'student_id', 'khmer_name', 'date_of_birth', 'gender', 
                  'phone_number', 'city', 'country', 'profile_picture', 'gpa', 'is_active']
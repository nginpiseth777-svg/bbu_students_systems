from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from students.models import Student
from .serializers import StudentSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['student_id', 'khmer_name', 'user__first_name', 'user__last_name']
    
    @action(detail=True, methods=['get'])
    def transcript(self, request, pk=None):
        student = self.get_object()
        enrollments = student.enrollments.filter(status='COMPLETED')
        return Response({
            'student_id': student.student_id,
            'khmer_name': student.khmer_name,
            'gpa': float(student.gpa),
            'completed_courses': enrollments.count(),
        })
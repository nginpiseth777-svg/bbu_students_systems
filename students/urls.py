from django.urls import path

from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('search/suggestions/', views.student_suggestions, name='student_suggestions'),
    path('register/', views.register_student, name='register'),
    path('<int:pk>/', views.student_detail, name='student_detail'),
    path('<int:pk>/update/', views.student_update, name='student_update'),
]
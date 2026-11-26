from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views  # ហៅ Auth Views មកប្រើ
from django.urls import include, path
from students import views as student_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', student_views.student_list, name='home'),
    # បន្ថែម Login URL ត្រង់នេះ ដើម្បីកុំឱ្យជាប់ error NoReverseMatch
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(template_name='students/login.html'),
        name='login',
    ),
    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(),
        name='logout',
    ),
    path('students/', include('students.urls')),
    path('courses/', include('courses.urls')),
    path('enrollments/', include('enrollments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
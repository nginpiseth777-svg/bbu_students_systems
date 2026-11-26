from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'khmer_name', 'get_english_name', 'gender', 'city', 'gpa', 'is_active']
    list_filter = ['is_active', 'gender', 'city']
    search_fields = ['student_id', 'khmer_name', 'user__first_name', 'user__last_name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_english_name(self, obj):
        return obj.user.get_full_name()
    get_english_name.short_description = "English Name"
from django.contrib import admin
from .models import TrainerRegistration, CourseInfo, CourseDetails

@admin.register(TrainerRegistration)
class TrainerRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'user__email', 'mobile')
    date_hierarchy = 'created_at'
    list_editable = ('status',)

@admin.register(CourseInfo)
class CourseInfoAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'trainer', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('course_name', 'trainer__username')
    prepopulated_fields = {'slug': ('course_name',)}
    date_hierarchy = 'created_at'
    raw_id_fields = ('trainer',)

@admin.register(CourseDetails)
class CourseDetailsAdmin(admin.ModelAdmin):
    list_display = ('course', 'created_at')
    search_fields = ('course__course_name', 'description')
    date_hierarchy = 'created_at'
    raw_id_fields = ('course',)

from django.contrib import admin

from main.models import Semester, Calendar

# Register your models here.

admin.site.register(Semester)

@admin.register(Calendar)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("name", "course_id", "group_id", "semester", "requests_amount")
    search_fields = ("name", "course_id", "group_id", "semester")

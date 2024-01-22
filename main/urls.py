from django.urls import path

from main.views import *

urlpatterns = [
    path("api/cron/update-calendars", cron_update_calendars, name="api/cron/update-calendars"),
    path("api/get-calendar", api_get_calendar, name="api/get-calendar"),
    path("api/get-groups", api_get_groups, name="api/get-groups"),
    path("api/get-courses", api_get_course, name="api/get-courses"),
    path("api/get-programs", api_get_programms, name="api/get-programs"),
    path("api/get-semesters", api_get_semesters, name="api/get-semesters"),
    path("about", index, name="about"),
    path("", index, name="index"),
]
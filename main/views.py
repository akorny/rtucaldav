from datetime import datetime

from requests import post
from django.shortcuts import render
from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.forms.models import model_to_dict
from django.conf import settings

from main.models import Semester, Calendar
from main.utils import update_calendar

def api_error_response(code: int, msg: str) -> JsonResponse:
    response = JsonResponse({"status": "err", "error": msg})
    response.status_code = code
    return response

# Create your views here.

def index(req: HttpRequest) -> HttpResponse:
    return render(req, "index.html")


def api_get_semesters(req: HttpRequest) -> HttpResponse:
    semesters = Semester.objects.all().order_by("-start_date")
    response = {
        "status": "ok",
        "semesters": [model_to_dict(s) for s in semesters]
    }
    return JsonResponse(response)


def api_get_programms(req: HttpRequest) -> HttpResponse:
    semester_id = req.GET.get("semester-id")
    if not semester_id:
        return api_error_response(400, "bad request")
    
    rq = post(f"{settings.NODARBIBAS_BASE_URL}/findProgramsBySemesterId", {
        "semesterId": semester_id
    })
    programs = rq.json()

    return JsonResponse({
        "status": "ok",
        "programs": programs
    })


def api_get_course(req: HttpRequest) -> HttpResponse:
    semester_id = req.GET.get("semester-id")
    program_id = req.GET.get("program-id")
    if not semester_id or not program_id:
        return api_error_response(400, "bad request")
    
    rq = post(f"{settings.NODARBIBAS_BASE_URL}/findCourseByProgramId", {
        "semesterId": semester_id,
        "programId": program_id
    })
    courses = rq.json()

    return JsonResponse({
        "status": "ok",
        "courses": courses
    })


def api_get_groups(req: HttpRequest) -> HttpResponse:
    semester_id = req.GET.get("semester-id")
    program_id = req.GET.get("program-id")
    course_id = req.GET.get("course-id")
    if not semester_id or not program_id or not course_id:
        return api_error_response(400, "bad request")
    
    rq = post(f"{settings.NODARBIBAS_BASE_URL}/findGroupByCourseId", {
        "semesterId": semester_id,
        "programId": program_id,
        "courseId": course_id
    })
    groups = rq.json()

    return JsonResponse({
        "status": "ok",
        "groups": groups
    })


def api_get_calendar(req: HttpRequest) -> HttpResponse:
    # Check whether a request is correct or not
    semester_id = req.GET.get("semester-id")
    program_id = req.GET.get("program-id")
    course_id = req.GET.get("course-id")
    semester_program_id = req.GET.get("semester-program-id")
    program_name = req.GET.get("program-name")
    group_id = req.GET.get("group-id")
    if not semester_id or not program_id or not course_id or not semester_program_id or not program_name or not group_id:
        return api_error_response(400, "bad request")
    
    # Check if calendar is published
    rq = post(f"{settings.NODARBIBAS_BASE_URL}/isSemesterProgramPublished", {
        "semesterProgramId": semester_program_id
    })
    is_published = rq.text == "true"

    if not is_published:
        return JsonResponse({
            "status": "ok",
            "published": False,
        })
    
    # Find appropriate semester
    try:
        semester = Semester.objects.get(rtu_id=semester_id)
    except Semester.DoesNotExist:
        return api_error_response(404, "Semester does not exist")

    # Find a calendar
    try:
        db_calendar = Calendar.objects.get(
            semester=semester,
            program_id=program_id,
            course_id=course_id,
            semester_program_id=semester_program_id
        )
        db_calendar.requests_amount += 1
        db_calendar.save()
    except Calendar.DoesNotExist:
        db_calendar = Calendar()
        db_calendar.semester = semester
        db_calendar.program_id = program_id
        db_calendar.course_id = course_id
        db_calendar.semester_program_id = semester_program_id
        db_calendar.group_id = group_id
        db_calendar.name = program_name
        db_calendar.save()
    
    calendar_path = update_calendar(db_calendar).replace("http://", "").split("/", 1)[1]
    calendar_url = settings.PUBLIC_CALDAV_URL_PREFIX + "/" + calendar_path
    
    return JsonResponse({"status": "ok", "calendar_url": calendar_url})


def cron_update_calendars(req: HttpRequest) -> HttpResponse:
    key = req.GET.get("key")
    if not key:
        return api_error_response(401, "not authorised")
    
    if key.lower() != settings.API_SECRET_KEY.lower():
        return api_error_response(401, "not authorised")
    
    calendars = Calendar.objects.filter(
        semester__end_date__gte=datetime.now(),
    )
    for calendar in calendars:
        update_calendar(calendar)

    return JsonResponse({"status": "ok"})
    


from hashlib import sha256
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta

from caldav import DAVClient
from caldav.lib import error
from requests import post, exceptions
from django.conf import settings

from main.models import Calendar, Semester, Event

class RTUEvent:
    def __init__(self, event: dict) -> None:
        self.id = event["eventId"]
        self.date_id = event["eventDateId"]
        self.name = event["eventTempName"]
        self.room = event["room"]["roomName"]

        event_date = date.fromtimestamp(event["eventDate"] / 1000)

        custom_start = event["customStart"]
        start_time = time(custom_start["hour"], custom_start["minute"], custom_start["second"])
        self.start_datetime = datetime.combine(event_date, start_time)

        custom_end = event["customEnd"]
        end_time = time(custom_end["hour"], custom_end["minute"], custom_end["second"])
        self.end_datetime = datetime.combine(event_date, end_time)
    
    def hash(self) -> bytes:
        event_start = self.start_datetime.isoformat() 
        event_end = self.end_datetime.isoformat() 
        string = f"{self.id}|{self.date_id}|{self.name}|{self.room}|{event_start}|{event_end}"
        return sha256(string.encode("utf-8")).digest()

    def check_id(self) -> str:
        return f"{self.id}|{self.date_id}"


def update_calendar(db_calendar: Calendar) -> str:
    # Open connection to CalDav
    with DAVClient(
        url=settings.CALDAV_URL, 
        username=settings.CALDAV_USERNAME,
        password=settings.CALDAV_PASSWORD,
    ) as client:
        semester = db_calendar.semester
        principal = client.principal()

        # Find an appropriate calendar (caldavc stands for CalDav calendar)
        try:
            caldav_calendar = principal.calendar(db_calendar.caldav_cname())
        except error.NotFoundError:
            caldav_calendar = principal.make_calendar(db_calendar.caldav_cname())
        
        month_date = semester.start_date
        semester_end_date = semester.end_date

        eventids_in_calendar = []
        while month_date.month == semester_end_date.month or month_date < semester_end_date:
            rs = post(f"{settings.NODARBIBAS_BASE_URL}/getSemesterProgEventList", {
                "semesterProgramId": db_calendar.semester_program_id,
                "year": str(month_date.year),
                "month": str(month_date.month),
            })
            try:
                events = rs.json()
            except exceptions.JSONDecodeError:
                if rs.text.strip() != "":
                    raise exceptions.JSONDecodeError(request=rs.request, response=rs)
                
                continue

            # Add or update events
            for eventdict in events:
                rtu_event = RTUEvent(eventdict)
                eventids_in_calendar.append(rtu_event.check_id())

                try:
                    db_event = Event.objects.get(
                        calendar=db_calendar,
                        date_id=rtu_event.date_id,
                        rtu_id=rtu_event.id
                    )
                except Event.DoesNotExist:
                    db_event = None
                
                # If hashes match - go to other event
                new_event_hash = rtu_event.hash()
                if db_event and new_event_hash == db_event.hash:
                    continue

                if not db_event:
                    # Add a new event
                    db_event = Event()
                    db_event.calendar = db_calendar
                    db_event.hash = new_event_hash
                    db_event.rtu_id = rtu_event.id
                    db_event.date_id = rtu_event.date_id
                    db_event.save()

                    caldav_calendar.save_event(
                        dtstart=rtu_event.start_datetime,
                        dtend=rtu_event.end_datetime,
                        summary=rtu_event.name,
                        location=rtu_event.room,
                        uid=db_event.caldav_id,
                        tzid="Europe/Riga"
                    )
                else:
                    # Update existing one
                    caldav_event = caldav_calendar.event(str(db_event.caldav_id))
                    caldav_event.icalendar_component["summary"] = rtu_event.name
                    caldav_event.icalendar_component["location"] = rtu_event.room
                    caldav_event.icalendar_component["dtstart"].dt = rtu_event.start_datetime
                    caldav_event.icalendar_component["dtend"].dt = rtu_event.end_datetime
                    caldav_event.save()

            month_date += relativedelta(months=1)

        # Remove non-existing events from calendar
        db_events = Event.objects.filter(calendar=db_calendar)
        for db_event in db_events:
            if db_event.check_id() in eventids_in_calendar:
                continue

            caldav_uid = db_event.caldav_id
            caldav_event = caldav_calendar.event(str(caldav_uid))
            caldav_event.delete()
            db_event.delete()

    return str(caldav_calendar.url)
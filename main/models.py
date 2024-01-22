from uuid import uuid4

from django.db import models

# Create your models here.

class Semester(models.Model):
    name = models.CharField(verbose_name="Nosaukums", max_length=100)
    rtu_id = models.PositiveIntegerField(verbose_name="Semestra RTU ID")
    start_date = models.DateField(verbose_name="Sākuma datums")
    end_date = models.DateField(verbose_name="Beigu datums")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Semestris"
        verbose_name_plural = "Semestri"


class Calendar(models.Model):
    name = models.CharField(verbose_name="Nosaukums", max_length=150)
    program_id = models.PositiveIntegerField(verbose_name="Programmas ID")
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        verbose_name="Semestris"
    )
    course_id = models.PositiveSmallIntegerField(verbose_name="Kursa ID")
    group_id = models.PositiveIntegerField(verbose_name="Grupas ID")
    semester_program_id = models.PositiveIntegerField(verbose_name="Semestra-Programmas ID", unique=True)
    requests_amount = models.PositiveBigIntegerField(verbose_name="Pieprasījumu skaits", default=1)

    def caldav_cname(self):
        return f"{self.name}, {self.semester.name}, {self.course_id}. kurss, {self.group_id}. grupa"

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Kalendārs"
        verbose_name_plural = "Kalendāri"


class Event(models.Model):
    calendar = models.ForeignKey(
        Calendar,
        on_delete=models.CASCADE,
        verbose_name="Kalendārs"
    )
    date_id = models.PositiveBigIntegerField(verbose_name="Datuma ID")
    rtu_id = models.PositiveBigIntegerField(verbose_name="Nodarbības ID")
    caldav_id = models.UUIDField(verbose_name="CalDav ID", default=uuid4, unique=True)
    hash = models.BinaryField(verbose_name="SHA256 event hash", max_length=32)

    def check_id(self):
        return f"{self.rtu_id}|{self.date_id}"
    
    class Meta:
        verbose_name = "Nodarbība"
        verbose_name_plural = "Nodarbības"

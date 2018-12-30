from django.db import models

# Create your models here.
from school_management_app.model_constants import UserType, AttendanceStatus, ExamStatus


class User(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    created = models.DateField(auto_now_add=True)
    username = models.CharField(max_length=10, null=False)
    password = models.CharField(max_length=20, null=False)
    type = models.CharField(max_length=4, choices=[(tag, tag.value) for tag in UserType], null=False)
    name = models.CharField(max_length=50, null=False)


class Attendance(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=2, choices=[(tag, tag.value) for tag in AttendanceStatus], null=False)


class Subjects(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=10, null=False)
    course = models.CharField(max_length=10, null=False)
    department = models.CharField(max_length=10, null=False)


class UserSubjectEngagment(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)


class ExamHistory(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=[(tag, tag.value) for tag in ExamStatus], null=False)


class StudentExamMarksRecords(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(ExamHistory, on_delete=models.CASCADE)

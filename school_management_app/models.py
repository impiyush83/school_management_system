from django.db import models
# Create your models here.
from django.db.models import Q

from school_management_app.constants.model_constants import UserType, AttendanceStatus, ExamStatus


class User(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    created = models.DateField(auto_now_add=True)
    username = models.CharField(max_length=10, null=False, unique=True)
    password = models.CharField(max_length=20, null=False)
    type = models.CharField(max_length=4, choices=[(tag, tag.value) for tag in UserType], null=False)
    name = models.CharField(max_length=50, null=False)
    enrolled = models.BooleanField(default=False, null=False)  # exclusively for students

    @classmethod
    def get_all_unenrolled_students(cls):
        return User.objects.filter(Q(enrolled=0) & Q(type='STUDENT')).order_by('id')

    @classmethod
    def get_all_enrolled_students(cls):
        return User.objects.filter(Q(enrolled=1) & Q(type='STUDENT')).order_by('id')

    @classmethod
    def insert_user(cls, data, user_type):
        user = User(name=data['name'], username=data['username'], password=data['password'], type=user_type)
        user.save()


class Subjects(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=10, null=False)
    course = models.CharField(max_length=10, null=False)
    department = models.CharField(max_length=10, null=False)

    @staticmethod
    def get_all_disctinct_courses_and_departments():
        courses = []
        all_records = Subjects.objects.all()
        for record in all_records:
            entry = str(record.department) + '->' + str(record.course)
            if entry not in courses:
                courses.append(entry)
        return courses

    @staticmethod
    def get_all_subjects():
        return Subjects.objects.all()  # returns queryset


class Attendance(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=2, choices=[(tag, tag.value) for tag in AttendanceStatus], null=False)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE, null=True)


class UserSubjectEngagment(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)

    @staticmethod
    def create_user_enrollment_entries(id, course):
        user = User.objects.get(id=id)
        subjects = Subjects.objects.filter(course=course)
        for subject in subjects:
            user_subject_engagment = UserSubjectEngagment(user=user, subject=subject)
            user_subject_engagment.save()


class ExamHistory(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=[(tag, tag.value) for tag in ExamStatus], null=False)

    @staticmethod
    def get_active_exams():
        return ExamHistory.objects.filter(status="ACTIVE")


class StudentExamMarksRecords(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(ExamHistory, on_delete=models.CASCADE)

# filter returns querysets
# get returns objects -> returns error if nothing found.

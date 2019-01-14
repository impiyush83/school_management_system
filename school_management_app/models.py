from django.db import models
# Create your models here.
from django.db.models import Q

from school_management_app.constants.model_constants import UserType, AttendanceStatus, ExamStatus
from school_management_app.util import encrypt_password, get_current_local_date


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
        encrypted_password = encrypt_password(data['password'])
        user = User(name=data['name'], username=data['username'], password=encrypted_password, type=user_type)
        user.save()

    @staticmethod
    def with_username(username):
        return User.objects.filter(username=username).first()


class Subjects(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=10, null=False)
    course = models.CharField(max_length=10, null=False)
    department = models.CharField(max_length=10, null=False)

    @staticmethod
    def get_all_distinct_courses_and_departments():
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

    @staticmethod
    def with_id(id):
        return Subjects.objects.filter(id=id).first()


class Attendance(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=2, choices=[(tag, tag.value) for tag in AttendanceStatus], null=False)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE, null=True)

    @staticmethod
    def get_todays_attendance(subjects):
        local_date = get_current_local_date()
        boolean_object_of_attendance = []
        for subject in subjects:
            if not Attendance.objects.filter(Q(date=local_date) & Q(subject=subject)):
                boolean_object_of_attendance.append(subject.id)
        return boolean_object_of_attendance

    @staticmethod
    def get_todays_attendance_with_subject(subject):
        local_date = get_current_local_date()
        return Attendance.objects.filter(Q(date=local_date) & Q(subject=subject))

    @staticmethod
    def bulk_insert(user_ids, subject_ids, status):
        local_date = get_current_local_date()
        for entry in range(0, len(user_ids)):
            record = Attendance(date=local_date, user_id=int(user_ids[entry]), status=status[entry],
                                subject_id=int(subject_ids[entry]))
            record.save()

    @staticmethod
    def get_attendance_of_student_for_all_subjects(user):
        return Attendance.objects.filter(user=user)


class UserSubjectEngagment(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    created = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)

    @staticmethod
    def with_student(student):
        return UserSubjectEngagment.objects.filter(user=student).first()

    @staticmethod
    def create_user_enrollment_entries(user_id, course):
        user = User.objects.get(id=user_id)
        subjects = Subjects.objects.filter(course=course)
        for subject in subjects:
            user_subject_engagment = UserSubjectEngagment(user=user, subject=subject)
            user_subject_engagment.save()

    @staticmethod
    def get_all_students_enrolled_with_subject_id(subject):
        return UserSubjectEngagment.objects.filter(subject=subject)

    @staticmethod
    def get_all_subjects_enrolled_with_user(user):
        user_subject_engagement = UserSubjectEngagment.objects.filter(user=user)
        subjects_enrolled = []
        for user_subject_object in user_subject_engagement:
            subjects_enrolled.append(user_subject_object.subject)
        return subjects_enrolled


class ExamHistory(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    created = models.DateField(auto_now_add=True)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=[(tag, tag.value) for tag in ExamStatus], null=False)
    marks_entered = models.BooleanField(null=False, default=0)

    @staticmethod
    def get_active_exams():
        return ExamHistory.objects.filter(status=ExamStatus.ACTIVE)

    @staticmethod
    def get_expired_exams():
        return ExamHistory.objects.filter(status=ExamStatus.EXPIRED)

    @staticmethod
    def insert_active_exam(subject):
        exam = ExamHistory(subject=subject, status=ExamStatus.ACTIVE)
        exam.save()

    @staticmethod
    def get_active_exams_with_subject_id(subject):
        return ExamHistory.objects.filter(Q(status=ExamStatus.ACTIVE) & Q(subject=subject))

    @staticmethod
    def get_exams_with_subject_ids(subjects):
        result = []
        for subject in subjects:
            results = ExamHistory.objects.filter(subject=subject)

    @staticmethod
    def finish_exam(subject):
        exams_to_finish = ExamHistory.objects.filter(subject=subject)
        for exam in exams_to_finish:
            ExamHistory.objects.filter(subject=subject).update(status=ExamStatus.EXPIRED)

    @staticmethod
    def update_with_id(id):
        ExamHistory.objects.filter(id=id).update(marks_entered=1)

    @staticmethod
    def with_id(id):
        return ExamHistory.objects.filter(id=id).first()


class StudentExamRecords(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(ExamHistory, on_delete=models.CASCADE)
    marks = models.IntegerField(null=False, default=-1)
    outof = models.IntegerField(default=100)
    exam_date = models.DateField(null=False)

    @staticmethod
    def add_entries(users, exam):
        for user in users:
            record = StudentExamRecords(user_id=user.user_id, exam=exam, exam_date=exam.created)
            record.save()

    @staticmethod
    def assign_marks(users, marks, exam):
        for index in range(len(users)):
            StudentExamRecords.objects.filter(Q(user_id=users[index]) & Q(exam=exam)).update(
                marks=marks[index])

    @staticmethod
    def get_exams_with_user(user):
        return StudentExamRecords.objects.filter(user=user)

# filter returns querysets
# get returns objects -> returns error if nothing found.

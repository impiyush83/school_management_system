import json

import jwt
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from school_management_app.constants.common_constants import COOKIE_NAME
from school_management_app.constants.response_constants import SUCCESS, AUTHENTICATION_ERROR, JWT_EXPIRED_COOKIE_ERROR, \
    DOES_NOT_EXIST_ERROR, ATTENDANCE_ALREADY_PRESENT, ONLY_TEACHER_ALLOWED
from school_management_app.models import User, Subjects, UserSubjectEngagment, ExamHistory, StudentExamRecords, \
    Attendance
from school_management_app.util import get_subject_id_from_active_exams, \
    get_list_of_users_marks
from school_management_project import settings


@api_view(["POST"])
@permission_classes((AllowAny,))
def engage_student(request):
    request_data = request.body
    request_data = request_data.decode('utf-8')
    request_data = json.loads(request_data)
    if COOKIE_NAME not in request.COOKIES:
        return AUTHENTICATION_ERROR
    cookie = request.COOKIES[COOKIE_NAME]
    try:
        data = jwt.decode(cookie, settings.SECRET_KEY)
    except:
        return JWT_EXPIRED_COOKIE_ERROR
    user = User.objects.get(id=data.get('user_id'))
    if user.type != 'TEACHER':
        return ONLY_TEACHER_ALLOWED
    try:
        id = request_data.get('id')
        course = request_data.get('course').split('->')[1]
        course = course.strip()
        UserSubjectEngagment.create_user_enrollment_entries(id, course)
        User.objects.filter(id=id).update(enrolled=1)
    except:
        return Response({'message': 'Error while enrollment !! DB ERROR !! '},
                        status=HTTP_409_CONFLICT)
    return SUCCESS


@api_view(["GET", "POST"])
@permission_classes((AllowAny,))
def create_exams(request):
    if COOKIE_NAME not in request.COOKIES:
        return AUTHENTICATION_ERROR
    cookie = request.COOKIES[COOKIE_NAME]
    try:
        data = jwt.decode(cookie, settings.SECRET_KEY)
    except:
        return JWT_EXPIRED_COOKIE_ERROR
    user = User.objects.get(id=data.get('user_id'))
    if user.type != 'TEACHER':
        return ONLY_TEACHER_ALLOWED

    subjects = Subjects.get_all_subjects()
    active_exams = ExamHistory.get_active_exams()
    active_examination_subjects = get_subject_id_from_active_exams(active_exams)
    return render(
        request,
        'create_exam.html',
        dict(
            subjects=subjects,
            active_examination_subjects=active_examination_subjects
        )
    )


@api_view(["POST"])
@permission_classes((AllowAny,))
def insert_exam(request):
    request_data = request.body
    request_data = request_data.decode('utf-8')
    request_data = json.loads(request_data)
    if COOKIE_NAME not in request.COOKIES:
        return AUTHENTICATION_ERROR
    cookie = request.COOKIES[COOKIE_NAME]
    try:
        data = jwt.decode(cookie, settings.SECRET_KEY)
    except:
        return JWT_EXPIRED_COOKIE_ERROR
    user = User.objects.get(id=data.get('user_id'))
    if user.type != 'TEACHER':
        return ONLY_TEACHER_ALLOWED
    try:
        subject_id = request_data.get('id')
        subject = Subjects.with_id(subject_id)
        students_appearing_for_exam = UserSubjectEngagment.get_all_students_enrolled_with_subject_id(subject)
        if not students_appearing_for_exam:
            return Response({'message': 'No students enrolled for this course'},
                            status=HTTP_404_NOT_FOUND)
        ExamHistory.insert_active_exam(subject)
        exam = ExamHistory.get_active_exams_with_subject_id(subject)[0]
        StudentExamRecords.add_entries(students_appearing_for_exam, exam)
    except:
        return Response({'message': 'Error while inserting exam !! DB ERROR !! '},
                        status=HTTP_409_CONFLICT)

    return SUCCESS


@api_view(["GET"])
@permission_classes((AllowAny,))
def close_active_exams_dashboard(request):
    if COOKIE_NAME not in request.COOKIES:
        return AUTHENTICATION_ERROR
    cookie = request.COOKIES[COOKIE_NAME]
    try:
        data = jwt.decode(cookie, settings.SECRET_KEY)
    except:
        return JWT_EXPIRED_COOKIE_ERROR
    user = User.objects.get(id=data.get('user_id'))
    if user.type != 'TEACHER':
        return ONLY_TEACHER_ALLOWED
    active_exams = ExamHistory.get_active_exams()
    subjects = []
    for exam in active_exams:
        subject = Subjects.with_id(exam.subject_id)
        subjects.append(subject)
    expired_exams = ExamHistory.get_expired_exams()
    return render(
        request,
        'finish_exam.html',
        dict(
            subjects=subjects,
            expired_exams=expired_exams
        )
    )


@api_view(["POST"])
@permission_classes((AllowAny,))
def close_active_exams(request):
    request_data = request.body
    request_data = request_data.decode('utf-8')
    request_data = json.loads(request_data)
    if COOKIE_NAME not in request.COOKIES:
        return AUTHENTICATION_ERROR
    cookie = request.COOKIES[COOKIE_NAME]
    try:
        data = jwt.decode(cookie, settings.SECRET_KEY)
    except:
        return JWT_EXPIRED_COOKIE_ERROR
    user = User.objects.get(id=data.get('user_id'))
    if user.type != 'TEACHER':
        return ONLY_TEACHER_ALLOWED
    try:
        subject_id = request_data.get('id')
        subject = Subjects.with_id(subject_id)
        ExamHistory.finish_exam(subject)
    except:
        return Response({'message': 'Error while enrollment !! DB ERROR !! '},
                        status=HTTP_409_CONFLICT)

    return SUCCESS


@api_view(["POST"])
@permission_classes((AllowAny,))
def assign_exam_marks_dashboard(request):
    if COOKIE_NAME not in request.COOKIES:
        return AUTHENTICATION_ERROR
    cookie = request.COOKIES[COOKIE_NAME]
    try:
        data = jwt.decode(cookie, settings.SECRET_KEY)
    except:
        return JWT_EXPIRED_COOKIE_ERROR
    user = User.objects.get(id=data.get('user_id'))
    if user.type != 'TEACHER':
        return ONLY_TEACHER_ALLOWED

    subject_id = int(request.data['subject_id'])
    exam_id = int(request.data['exam_id'])
    subject = Subjects.with_id(subject_id)
    marks = [i for i in range(0, 101)]
    students = UserSubjectEngagment.get_all_students_enrolled_with_subject_id(subject)
    return render(
        request,
        'assign_marks.html',
        dict(
            students=students,
            exam_id=exam_id,
            max_marks=marks
        )
    )


@api_view(["POST"])
@permission_classes((AllowAny,))
def assign_exam_marks(request):
    if COOKIE_NAME not in request.COOKIES:
        return AUTHENTICATION_ERROR
    cookie = request.COOKIES[COOKIE_NAME]
    try:
        data = jwt.decode(cookie, settings.SECRET_KEY)
    except:
        return JWT_EXPIRED_COOKIE_ERROR
    user = User.objects.get(id=data.get('user_id'))
    if user.type != 'TEACHER':
        return ONLY_TEACHER_ALLOWED
    formdata = request.data['data']
    if formdata:
        exam_id = int(formdata[1]['exam_id'])
        exam = ExamHistory.with_id(exam_id)
        subject_id = exam.subject.id
        subject = Subjects.with_id(subject_id)
        users, marks = get_list_of_users_marks(formdata)
        StudentExamRecords.assign_marks(users, marks, exam)
        ExamHistory.update_with_id(exam_id)
        return SUCCESS
    else:
        return DOES_NOT_EXIST_ERROR


@api_view(["GET"])
@permission_classes((AllowAny,))
def view_attendance_dashboard(request):
    if COOKIE_NAME not in request.COOKIES:
        return AUTHENTICATION_ERROR
    cookie = request.COOKIES[COOKIE_NAME]
    try:
        data = jwt.decode(cookie, settings.SECRET_KEY)
    except:
        return JWT_EXPIRED_COOKIE_ERROR
    user = User.objects.get(id=data.get('user_id'))
    if user.type != 'TEACHER':
        return ONLY_TEACHER_ALLOWED
    subjects = Subjects.get_all_subjects()
    attendance = Attendance.get_todays_attendance(subjects)
    return render(
        request,
        'mark_attendance_dashboard.html',
        dict(
            subjects=subjects,
            attendance=attendance
        )
    )


@api_view(["POST"])
@permission_classes((AllowAny,))
def take_attendance_for_subject(request):
    if COOKIE_NAME not in request.COOKIES:
        return AUTHENTICATION_ERROR
    cookie = request.COOKIES[COOKIE_NAME]
    try:
        data = jwt.decode(cookie, settings.SECRET_KEY)
    except:
        return JWT_EXPIRED_COOKIE_ERROR
    user = User.objects.get(id=data.get('user_id'))
    if user.type != 'TEACHER':
        return ONLY_TEACHER_ALLOWED
    subject_id = int(request.data['id'])
    subject = Subjects.with_id(subject_id)
    attendance = Attendance.get_todays_attendance_with_subject(subject)
    if attendance:
        return ATTENDANCE_ALREADY_PRESENT
    users = UserSubjectEngagment.get_all_students_enrolled_with_subject_id(subject)
    if not users:
        return NO_USER_ENROLLED_FOR_THIS_COURSE
    return render(
        request,
        'subject_attendance.html',
        dict(
            users=users,
            subject=subject
        )
    )


@api_view(["POST"])
@permission_classes((AllowAny,))
def insert_student_attendance(request):
    if COOKIE_NAME not in request.COOKIES:
        return AUTHENTICATION_ERROR
    cookie = request.COOKIES[COOKIE_NAME]
    try:
        data = jwt.decode(cookie, settings.SECRET_KEY)
    except:
        return JWT_EXPIRED_COOKIE_ERROR
    user = User.objects.get(id=data.get('user_id'))
    if user.type != 'TEACHER':
        return ONLY_TEACHER_ALLOWED

    user_id = request.data.get('user_id')
    subject_id = request.data.get('subject_id')
    status = request.data.get('status')
    Attendance.bulk_insert(user_id, subject_id, status)
    return redirect('/user/home/')


@api_view(["GET"])
@permission_classes((AllowAny,))
def enroll_student(request):
    if COOKIE_NAME not in request.COOKIES:
        return AUTHENTICATION_ERROR
    cookie = request.COOKIES[COOKIE_NAME]
    try:
        data = jwt.decode(cookie, settings.SECRET_KEY)
    except:
        return JWT_EXPIRED_COOKIE_ERROR
    user = User.objects.get(id=data.get('user_id'))
    if user.type != 'TEACHER':
        return ONLY_TEACHER_ALLOWED
    unenrolled_students = User.get_all_unenrolled_students()
    enrolled_students = User.get_all_enrolled_students()
    try:
        courses = Subjects.get_all_disctinct_courses_and_departments()
    except:
        return DOES_NOT_EXIST_ERROR
    return render(
        request,
        'enroll_student.html',
        dict(
            unenrolled_students=unenrolled_students,
            enrolled_students=enrolled_students,
            courses=courses
        )
    )

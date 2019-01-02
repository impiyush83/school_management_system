import json

import jwt
from django.shortcuts import render
from django.utils.datetime_safe import datetime
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT

from school_management_app.constants.common_constants import COOKIE_NAME, MASTER_KEY
from school_management_app.constants.model_constants import UserType
from school_management_app.constants.response_constants import SUCCESS, AUTHENTICATION_ERROR, JWT_EXPIRED_COOKIE_ERROR, \
    USER_ALREADY_PRESENT, DOES_NOT_EXIST_ERROR
from school_management_app.login import get_user
from school_management_app.models import User, Subjects, UserSubjectEngagment, ExamHistory, StudentExamRecords
from school_management_app.util import get_subject_id_from_active_exams
from school_management_project import settings


# Create your views here.

@api_view(['GET', ])
@permission_classes((AllowAny,))
def index(request):
    return render(request, 'index.html', {})


# api_view and permission_classes are part of django-restful
@csrf_exempt
@api_view(['POST', ])
@permission_classes((AllowAny,))
def add_user(request):
    request_data = request.body
    request_data = request_data.decode('utf-8')
    data = json.loads(request_data)
    if data.get("type") == 'Teacher':
        if not data.get("master_key"):
            return Response({'message': 'Bad Request'},
                            status=HTTP_400_BAD_REQUEST)
        if data.get('master_key') != MASTER_KEY:
            return Response({'message': 'Bad Master Key'},
                            status=HTTP_400_BAD_REQUEST)
        try:
            User.insert_user(data, UserType.TEACHER.value)
        except:
            return USER_ALREADY_PRESENT

    else:
        try:
            User.insert_user(data, UserType.PARENT.value) \
                if data.get("type") == 'Parent' else User.insert_user(data, UserType.STUDENT.value)
        except:
            return USER_ALREADY_PRESENT
    return SUCCESS


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def user_login(request):
    request_data = request.body
    request_data = request_data.decode('utf-8')
    data = json.loads(request_data)
    username = data.get("username")
    password = data.get("password")
    if username is None or password is None:
        return Response({'message': 'Please provide both username and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = get_user(username=username)
    if not user:
        return Response({'message': 'User not found'},
                        status=HTTP_404_NOT_FOUND)
    if user.password != password:
        return Response({'message': 'Invalid credentials'},
                        status=HTTP_401_UNAUTHORIZED)
    payload = dict(user_id=user.id, username=user.username, exp=datetime.utcnow() + settings.JWT_COOKIE_EXPIRATION)
    # create payload of username, primary key which is id and expiration time.
    token = jwt.encode(payload, settings.SECRET_KEY).decode('utf-8')
    SUCCESS.set_cookie(COOKIE_NAME, token)
    return SUCCESS


@api_view(["GET"])
@permission_classes((AllowAny,))
def render_homepage(request):
    if COOKIE_NAME in request.COOKIES:
        cookie = request.COOKIES[COOKIE_NAME]
        try:
            data = jwt.decode(cookie, settings.SECRET_KEY)
        except:
            return JWT_EXPIRED_COOKIE_ERROR
        user = User.objects.get(id=data.get('user_id'))
        return render(request, 'homepage.html', dict(user=user))
    else:
        return AUTHENTICATION_ERROR


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def user_logout(request):
    if COOKIE_NAME in request.COOKIES:
        cookie = request.COOKIES[COOKIE_NAME]
        try:
            data = jwt.decode(cookie, settings.SECRET_KEY)
        except:
            return JWT_EXPIRED_COOKIE_ERROR

        SUCCESS.set_cookie(COOKIE_NAME, expires=0)
        return SUCCESS
    else:
        return AUTHENTICATION_ERROR


@api_view(["GET"])
@permission_classes((AllowAny,))
def enroll_student(request):
    if COOKIE_NAME in request.COOKIES:
        cookie = request.COOKIES[COOKIE_NAME]
        try:
            data = jwt.decode(cookie, settings.SECRET_KEY)
        except:
            return JWT_EXPIRED_COOKIE_ERROR
        user = User.objects.get(id=data.get('user_id'))
        if user.type != 'TEACHER':
            return Response({'message': 'Only Authorized for teacher'},
                            status=HTTP_401_UNAUTHORIZED)
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
    else:
        return AUTHENTICATION_ERROR


@api_view(["POST"])
@permission_classes((AllowAny,))
def engage_student(request):
    request_data = request.body
    request_data = request_data.decode('utf-8')
    request_data = json.loads(request_data)
    if COOKIE_NAME in request.COOKIES:
        cookie = request.COOKIES[COOKIE_NAME]
        try:
            data = jwt.decode(cookie, settings.SECRET_KEY)
        except:
            return JWT_EXPIRED_COOKIE_ERROR
        user = User.objects.get(id=data.get('user_id'))
        if user.type != 'TEACHER':
            return Response({'message': 'Only Authorized for teacher'},
                            status=HTTP_401_UNAUTHORIZED)
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
    else:
        return AUTHENTICATION_ERROR


@api_view(["GET", "POST"])
@permission_classes((AllowAny,))
def create_exams(request):
    if COOKIE_NAME in request.COOKIES:
        cookie = request.COOKIES[COOKIE_NAME]
        try:
            data = jwt.decode(cookie, settings.SECRET_KEY)
        except:
            return JWT_EXPIRED_COOKIE_ERROR
        user = User.objects.get(id=data.get('user_id'))
        if user.type != 'TEACHER':
            return Response({'message': 'Only Authorized for teacher'},
                            status=HTTP_401_UNAUTHORIZED)

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
    else:
        return AUTHENTICATION_ERROR


@api_view(["POST"])
@permission_classes((AllowAny,))
def insert_exam(request):
    request_data = request.body
    request_data = request_data.decode('utf-8')
    request_data = json.loads(request_data)
    if COOKIE_NAME in request.COOKIES:
        cookie = request.COOKIES[COOKIE_NAME]
        try:
            data = jwt.decode(cookie, settings.SECRET_KEY)
        except:
            return JWT_EXPIRED_COOKIE_ERROR
        user = User.objects.get(id=data.get('user_id'))
        if user.type != 'TEACHER':
            return Response({'message': 'Only Authorized for teacher'},
                            status=HTTP_401_UNAUTHORIZED)
        try:
            subject_id = request_data.get('id')
            subject = Subjects.with_id(subject_id)[0]
            ExamHistory.insert_active_exam(subject)
            students_appearing_for_exam = UserSubjectEngagment.get_all_students_enrolled_with_subject_id(subject)
            exam = ExamHistory.get_active_exams_with_subject_id(subject)[0]
            StudentExamRecords.add_entries(students_appearing_for_exam, exam)
        except:
            return Response({'message': 'Error while enrollment !! DB ERROR !! '},
                            status=HTTP_409_CONFLICT)

        return SUCCESS
    else:
        return AUTHENTICATION_ERROR


@api_view(["GET"])
@permission_classes((AllowAny,))
def close_active_exams_dashboard(request):
    if COOKIE_NAME in request.COOKIES:
        cookie = request.COOKIES[COOKIE_NAME]
        try:
            data = jwt.decode(cookie, settings.SECRET_KEY)
        except:
            return JWT_EXPIRED_COOKIE_ERROR
        user = User.objects.get(id=data.get('user_id'))
        if user.type != 'TEACHER':
            return Response({'message': 'Only Authorized for teacher'},
                            status=HTTP_401_UNAUTHORIZED)
        active_exams = ExamHistory.get_active_exams()
        subjects = []
        for exam in active_exams:
            subject = Subjects.with_id(exam.subject_id)[0]
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
    else:
        return AUTHENTICATION_ERROR


@api_view(["POST"])
@permission_classes((AllowAny,))
def close_active_exams(request):
    request_data = request.body
    request_data = request_data.decode('utf-8')
    request_data = json.loads(request_data)
    if COOKIE_NAME in request.COOKIES:
        cookie = request.COOKIES[COOKIE_NAME]
        try:
            data = jwt.decode(cookie, settings.SECRET_KEY)
        except:
            return JWT_EXPIRED_COOKIE_ERROR
        user = User.objects.get(id=data.get('user_id'))
        if user.type != 'TEACHER':
            return Response({'message': 'Only Authorized for teacher'},
                            status=HTTP_401_UNAUTHORIZED)
        try:
            subject_id = request_data.get('id')
            subject = Subjects.with_id(subject_id)[0]
            ExamHistory.finish_exam(subject)
        except:
            return Response({'message': 'Error while enrollment !! DB ERROR !! '},
                            status=HTTP_409_CONFLICT)

        return SUCCESS
    else:
        return AUTHENTICATION_ERROR


@api_view(["POST"])
@permission_classes((AllowAny,))
def assign_exam_marks_dashboard(request):
    if COOKIE_NAME in request.COOKIES:
        cookie = request.COOKIES[COOKIE_NAME]
        try:
            data = jwt.decode(cookie, settings.SECRET_KEY)
        except:
            return JWT_EXPIRED_COOKIE_ERROR
        user = User.objects.get(id=data.get('user_id'))
        if user.type != 'TEACHER':
            return Response({'message': 'Only Authorized for teacher'},
                            status=HTTP_401_UNAUTHORIZED)
        import pdb
        pdb.set_trace()
        subject_id = int(request.data['subject_id'])
        exam_id = int(request.data['exam_id'])
        subject = Subjects.with_id(subject_id)[0]
        students = UserSubjectEngagment.get_all_students_enrolled_with_subject_id(subject)
        return render(
            request,
            'assign_marks.html',
            dict(
                students=students,
                exam_id=exam_id
            )
        )
    else:
        return AUTHENTICATION_ERROR

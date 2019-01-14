import jwt
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED

from school_management_app.constants.common_constants import COOKIE_NAME, AttendanceCustomObject
from school_management_app.constants.response_constants import AUTHENTICATION_ERROR, JWT_EXPIRED_COOKIE_ERROR, \
    ONLY_STUDENT_ALLOWED, ONLY_PARENT_ALLOWED, INVALID_CREDENTIALS
from school_management_app.models import User, UserSubjectEngagment, Attendance, StudentExamRecords
from school_management_app.util import get_current_local_date_in_datetime_format, check_encrypted_password
from school_management_project import settings


@api_view(["POST"])
@permission_classes((AllowAny,))
def select_student_to_view_exam_marks(request):
    if COOKIE_NAME not in request.COOKIES:
        return AUTHENTICATION_ERROR
    cookie = request.COOKIES[COOKIE_NAME]
    try:
        data = jwt.decode(cookie, settings.SECRET_KEY)
    except:
        return JWT_EXPIRED_COOKIE_ERROR
    parent = User.objects.get(id=data.get('user_id'))
    if parent.type != 'PARENT':
        return ONLY_PARENT_ALLOWED

    username = request.data.get('student_username2')
    password = request.data.get('student_password2')
    user = User.with_username(username)
    if not user:
        return Response({'message': 'No such student !!! '},
                        status=HTTP_404_NOT_FOUND)

    if not check_encrypted_password(password, user.password):
        return INVALID_CREDENTIALS
    if not user.enrolled:
        return Response({'message': 'User not enrolled in course !!! '},
                        status=HTTP_404_NOT_FOUND)

    exams = StudentExamRecords.get_exams_with_user(user)

    return render(
        request,
        'view_exam_marks.html',
        dict(
            exams=exams
        )
    )


@api_view(["POST"])
@permission_classes((AllowAny,))
def select_student_to_view_attendance(request):
    if COOKIE_NAME not in request.COOKIES:
        return AUTHENTICATION_ERROR
    cookie = request.COOKIES[COOKIE_NAME]
    try:
        data = jwt.decode(cookie, settings.SECRET_KEY)
    except:
        return JWT_EXPIRED_COOKIE_ERROR
    parent = User.objects.get(id=data.get('user_id'))
    if parent.type != 'PARENT':
        return ONLY_PARENT_ALLOWED
    username = request.data.get('student_username1')
    password = request.data.get('student_password1')
    user = User.with_username(username)
    if not user:
        return Response({'message': 'No such student !!! '},
                        status=HTTP_404_NOT_FOUND)

    if not check_encrypted_password(password, user.password):
        return INVALID_CREDENTIALS
    if not user.enrolled:
        return Response({'message': 'User not enrolled in course !!! '},
                        status=HTTP_404_NOT_FOUND)

    user_subject_engagement_record = UserSubjectEngagment.with_student(user)
    user_enrollment_date = user_subject_engagement_record.created
    local_datetime = get_current_local_date_in_datetime_format()
    local_date = local_datetime.date()
    total_days = local_date - user_enrollment_date
    total_attendance_of_user = Attendance.get_attendance_of_student_for_all_subjects(user)
    subjects_enrolled = UserSubjectEngagment.get_all_subjects_enrolled_with_user(user)
    resp_data = {}
    for subject in subjects_enrolled:
        resp_data[subject.id] = 0
    for record in total_attendance_of_user:
        resp_data[record.subject.id] += 1
    attendance = []
    for key in resp_data:
        attendance_obj = AttendanceCustomObject(key, resp_data[key])
        attendance.append(attendance_obj)
    return render(
        request,
        'view_attendance.html',
        dict(
            total_days=total_days.days + 1,
            attendance=attendance

        )
    )

import json

import jwt
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT

from school_management_app.constants.common_constants import COOKIE_NAME
from school_management_app.constants.response_constants import SUCCESS, AUTHENTICATION_ERROR, JWT_EXPIRED_COOKIE_ERROR, \
    DOES_NOT_EXIST_ERROR, ATTENDANCE_ALREADY_PRESENT, NO_USER_ENROLLED_FOR_THIS_COURSE, ONLY_STUDENT_ALLOWED
from school_management_app.models import User, Subjects, UserSubjectEngagment, ExamHistory, StudentExamRecords, \
    Attendance
from school_management_app.util import get_subject_id_from_active_exams, \
    get_list_of_users_marks, get_current_local_date
from school_management_project import settings


@api_view(["GET"])
@permission_classes((AllowAny,))
def view_attendance(request):
    if COOKIE_NAME not in request.COOKIES:
        return AUTHENTICATION_ERROR
    cookie = request.COOKIES[COOKIE_NAME]
    try:
        data = jwt.decode(cookie, settings.SECRET_KEY)
    except:
        return JWT_EXPIRED_COOKIE_ERROR
    user = User.objects.get(id=data.get('user_id'))
    if user.type != 'STUDENT':
        return ONLY_STUDENT_ALLOWED
    user_creation_date = user.created
    local_date = get_current_local_date()
    total_attendance_of_user = Attendance.get_attendance_of_student_for_all_subjects(user)
    subjects_enrolled = UserSubjectEngagment.get_all_students_enrolled_with_user(user)
    import pdb
    pdb.set_trace()
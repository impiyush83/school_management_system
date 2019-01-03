import json

import jwt
from django.shortcuts import render
from django.utils.datetime_safe import datetime
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST

from school_management_app.constants.common_constants import COOKIE_NAME, MASTER_KEY
from school_management_app.constants.model_constants import UserType
from school_management_app.constants.response_constants import SUCCESS, AUTHENTICATION_ERROR, JWT_EXPIRED_COOKIE_ERROR, \
    USER_ALREADY_PRESENT
from school_management_app.login import get_user
from school_management_app.models import User
from school_management_app.util import check_encrypted_password
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
    if not check_encrypted_password(data['password'], user.password):
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
    if COOKIE_NAME not in request.COOKIES:
        return AUTHENTICATION_ERROR
    cookie = request.COOKIES[COOKIE_NAME]
    try:
        data = jwt.decode(cookie, settings.SECRET_KEY)
    except:
        return JWT_EXPIRED_COOKIE_ERROR
    user = User.objects.get(id=data.get('user_id'))
    return render(request, 'homepage.html', dict(user=user))


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def user_logout(request):
    if COOKIE_NAME not in request.COOKIES:
        return AUTHENTICATION_ERROR
    cookie = request.COOKIES[COOKIE_NAME]
    try:
        data = jwt.decode(cookie, settings.SECRET_KEY)
    except:
        return JWT_EXPIRED_COOKIE_ERROR

    SUCCESS.set_cookie(COOKIE_NAME, expires=0)
    return SUCCESS




import json

import jwt
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.datetime_safe import datetime
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from school_management_app.constants.common_constants import COOKIE_NAME
from school_management_app.constants.model_constants import UserType
from school_management_app.login import check_authenticated
from school_management_app.models import User
from school_management_app.responses import bad_request, resource_conflict, decode_error, cookie_not_found
from school_management_project import settings


# Create your views here.


def index(request):
    return render(request, 'index.html', {})


@csrf_exempt
def add_user(request):
    request_data = request.body
    request_data = request_data.decode('utf-8')
    data = json.loads(request_data)
    if data.get("type") == 'Teacher':
        if not data.get("master_key"):
            return bad_request("Master Key not found")
        try:
            User.insert_user(data, UserType.TEACHER.value)
        except:
            return resource_conflict("Resource already present")

    else:
        if data.get("type") == 'Parent':
            try:
                User.insert_user(data, UserType.PARENT.value)
            except:
                return resource_conflict("Resource already present")
        else:
            try:
                User.insert_user(data, UserType.STUDENT.value)
            except:
                return resource_conflict("Resource already present")
    return HttpResponse("Success")


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
        return Response({'error': 'Please provide both username and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = check_authenticated(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)
    payload = dict(user_id=user.id, username=user.username, exp=datetime.utcnow() + settings.JWT_COOKIE_EXPIRATION)
    # create payload of username, primary key which is id and expiration time.
    token = jwt.encode(payload, settings.SECRET_KEY)
    response = HttpResponse()
    response.set_cookie(COOKIE_NAME, token)
    return response


def render_homepage(request):
    if COOKIE_NAME in request.COOKIES:
        cookie = request.COOKIES[COOKIE_NAME]
        cookie = cookie[2:-1]
        try:
            data = jwt.decode(cookie, settings.SECRET_KEY)
        except:
            return decode_error("Authentication Error")
        user = User.objects.get(id=data.get('user_id'))
        return render(request, 'homepage.html', dict(user=user))
    else:
        return cookie_not_found("Authentication Error")


@csrf_exempt
def user_logout(request):
    if COOKIE_NAME in request.COOKIES:
        cookie = request.COOKIES[COOKIE_NAME]
        cookie = cookie[2:-1]
        try:
            data = jwt.decode(cookie, settings.SECRET_KEY)
        except:
            return decode_error("Authentication Error")
        response = HttpResponse()
        response.set_cookie(COOKIE_NAME, expires=0)
        return response
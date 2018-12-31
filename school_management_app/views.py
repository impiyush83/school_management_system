import json

import jwt
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, user_logged_in
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.template import RequestContext

from django.views.decorators.csrf import csrf_protect, csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK
from rest_framework_jwt.utils import jwt_payload_handler

from school_management_app.constants.model_constants import UserType
from school_management_app.login import check_authenticated
from school_management_app.models import User
from django.core.exceptions import (
    NON_FIELD_ERRORS, FieldDoesNotExist, FieldError, MultipleObjectsReturned,
    ObjectDoesNotExist, ValidationError,
)

from school_management_app.responses import bad_request, resource_conflict
from school_management_project import settings


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
    payload = jwt_payload_handler(user)
    token = jwt.encode(payload, settings.SECRET_KEY)
    user_details = {}
    user_details['name'] = "%s" % (user.name)
    user_details['id'] = user.id
    user_details['type'] = user.type
    user_details['token'] = token
    return Response(user_details, status=status.HTTP_200_OK)

import json

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.template import RequestContext

from django.views.decorators.csrf import csrf_protect, csrf_exempt

from school_management_app.constants.model_constants import UserType
from school_management_app.models import User
from django.core.exceptions import (
    NON_FIELD_ERRORS, FieldDoesNotExist, FieldError, MultipleObjectsReturned,
    ObjectDoesNotExist, ValidationError,
)

from school_management_app.responses import bad_request, resource_conflict


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
            User.insert_user(data, UserType.TEACHER)
        except:
            return resource_conflict("Resource already present")

    else:
        if data.get("type") == 'Parent':
            try:
                User.insert_user(data, UserType.PARENT)
            except:
                return resource_conflict("Resource already present")
        else:
            try:
                User.insert_user(data, UserType.STUDENT)
            except:
                return resource_conflict("Resource already present")
    return HttpResponse("Success")


@csrf_exempt
def user_login(request):
    request_data = request.body
    request_data = request_data.decode('utf-8')
    data = json.loads(request_data)
    import pdb
    pdb.set_trace()
    pass

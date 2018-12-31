import json

from django.http import HttpResponse


def bad_request(message):
    response = HttpResponse(json.dumps({'message': message}),
                            content_type='application/json')
    response.status_code = 400
    return response


def resource_conflict(message):
    response = HttpResponse(json.dumps({'message': message}),
                            content_type='application/json')
    response.status_code = 409
    return response

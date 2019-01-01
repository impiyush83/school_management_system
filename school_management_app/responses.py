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


def cookie_not_found(message):
    response = HttpResponse(json.dumps({'message': message}),
                            content_type='application/json')
    response.status_code = 404
    return response


def decode_error(message):
    response = HttpResponse(json.dumps({'message': message}),
                            content_type='application/json')
    response.status_code = 401
    return response
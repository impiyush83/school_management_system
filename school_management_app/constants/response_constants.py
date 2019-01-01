from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT

SUCCESS = Response({'message': 'Success'}, status=HTTP_200_OK)
AUTHENTICATION_ERROR = Response(
    {'message': 'Cookie not found'},
    status=HTTP_401_UNAUTHORIZED
)
JWT_EXPIRED_COOKIE_ERROR = Response({'message': 'JWT Expired'},
                                    status=HTTP_401_UNAUTHORIZED)
USER_ALREADY_PRESENT = Response({'message': 'User already present'},
                                status=HTTP_409_CONFLICT)

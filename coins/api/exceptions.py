from rest_framework.exceptions import *
from rest_framework import status

class NotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Not Found'

    def __init__(self, detail=None):
        self.detail = detail or self.default_detail

class Gone(APIException):
    status_code = status.HTTP_410_GONE
    default_detail = 'Gone'

    def __init__(self, detail=None):
        self.detail = detail or self.default_detail

class ServerError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Internal Server Error'

    def __init__(self, detail=None):
        self.detail = detail or self.default_detail

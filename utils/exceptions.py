# core/exceptions.py
from rest_framework.views import exception_handler
from utils.c_response import custom_response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None and response.status_code == 429:
        return custom_response(False, "Juda ko‘p urinishlar! Keyinroq urinib ko‘ring.", {}, 429)
    return response

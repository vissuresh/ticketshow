from werkzeug.exceptions import HTTPException
from flask import make_response
import json
from datetime import datetime

class NotFoundError(HTTPException):
    def __init__(self, status_code, error_code = None, error_message = None):
        
        if error_code and error_message:
            data = { "error_code" : error_code, "error_message": error_message}
            self.response = make_response(json.dumps(data), status_code)

        else:
            self.response = make_response('', status_code)

class AccessDeniedError(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('', status_code)

class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        data = { "error_code" : error_code, "error_message": error_message }
        self.response = make_response(json.dumps(data), status_code)

class SchemaValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        data = { "error_code" : error_code, "error_message": error_message }
        self.response = make_response(json.dumps(data), status_code)


def validate_tags(tags):
    import string
    error_message = None

    for tag in tags.split(' '):
        if len(tag) > 16:
            error_message='Length of tag must be <= 16'
        for c in tag:
            if c in string.punctuation:
                error_message= 'Tags cannot contain punctuation'
    
    return error_message

def validate_timing(timing):
    error_message = None
    timing_obj = None

    try:
        timing_obj = datetime.strptime(timing, "%H:%M %d-%m-%Y")
        if timing_obj <= datetime.now():
            error_message = "Timing cannot be in the past!"
    except:
        error_message = 'Timing format to be in  {} '.format("%H:%M %d-%m-%Y")
    
    return timing_obj, error_message
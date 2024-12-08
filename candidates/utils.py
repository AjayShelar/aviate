from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from django.http import JsonResponse



# Custom Exception Handler
def custom_exception_handler(exc, context):
    """
    Custom exception handler to include an 'error' key in validation errors.
    """
    # Call the default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Modify the response for validation errors
        if isinstance(exc, ValidationError):
            response.data = {
                "error": response.data,  # Include the validation error details under 'error'
                "status_code": response.status_code
            }
        else:
            response.data["error"] = "An unexpected error occurred."

    return response




# Utility: Standardized Error Response Formatter
def format_error_response(message, status=400):
    """
    Returns a standardized error response format.
    """
    return {"error": message, "status": status}
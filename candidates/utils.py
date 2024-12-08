from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from django.http import JsonResponse



# Custom Exception Handler
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # Handle DRF exceptions
    if response is not None:
        return response

    # Handle generic validation errors
    if isinstance(exc, ValidationError):
        return JsonResponse({"error": exc.detail}, status=400)

    # Handle other exceptions
    return JsonResponse({"error": "An unexpected error occurred."}, status=500)




# Utility: Standardized Error Response Formatter
def format_error_response(message, status=400):
    """
    Returns a standardized error response format.
    """
    return {"error": message, "status": status}
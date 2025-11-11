from rest_framework.response import Response


def custom_response(success, message, data=None, status_code=200):
    """
        sdhfsdijfksd
    """
    return Response({
        "success": success,
        "message": message,
        "data": data or {}
    }, status=status_code)

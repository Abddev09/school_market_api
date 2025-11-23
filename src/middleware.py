from django.conf import settings
from django.http import JsonResponse

class InfinityHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        header_value = request.headers.get("Google-Autheration")
        if not header_value:
            return JsonResponse({"detail":"sehrli so'zni ayt."})
        if header_value != settings.SHIFR_KEY:
            return JsonResponse({"detail": "Xatolik: chuchvara hom sanaldi Bye bye"}, status=403)

        response = self.get_response(request)
        return response

# core/throttling.py
from rest_framework.throttling import SimpleRateThrottle

class ErrorOnlyThrottle(SimpleRateThrottle):
    scope = 'error'

    def get_cache_key(self, request, view):
        # IP asosida throttling; xohlasang user.id bilan ham qo'shish mumkin
        return self.get_ident(request)

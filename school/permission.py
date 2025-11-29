from rest_framework.permissions import BasePermission


class GradePermission(BasePermission):
    def has_permission(self, request, view):
        # Role 3 bo‘lsa (masalan, o‘quvchi) — ruxsat yo‘q
        if not request.user.is_authenticated:
            return False

        return request.user.role in [0, 1, 2]

class ClassPermission(BasePermission):
    def has_permission(self, request, view):
        # Role 3 bo‘lsa (masalan, o‘quvchi) — ruxsat yo‘q
        if not request.user.is_authenticated:
            return False

        return request.user.role in [0, 1, 2]

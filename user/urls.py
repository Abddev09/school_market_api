from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthViews,
    UserViews,
    ImportStudents,
    ChangePasswordView,
    TeacherView,
    StudentUserViews,
    StudentUserViewss,
    TeacherUserViews,
)

# 🔹 Router faqat ModelViewSet uchun
router = DefaultRouter()
router.register(r'users', UserViews, basename='users')

urlpatterns = [
    path('login/', AuthViews.as_view(), name='login'),
    path('students/import/', ImportStudents.as_view(), name='import-students'),
    path('reset-password/', ChangePasswordView.as_view(), name='user-reset-password'),
    path("my-students/",TeacherView.as_view(),name="my-students"),
    path("student/users/",StudentUserViews.as_view(), name="student-users"),
    path("all-students",StudentUserViewss.as_view(),name="all-students"),
    path("all-teachers", TeacherUserViews.as_view(),name="all-teacher"),
    path('', include(router.urls)),
]

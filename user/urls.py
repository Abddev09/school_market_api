from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthViews,
    UserViews,
    ImportStudents,
    ChangePasswordView,
    TeacherView
)

# 🔹 Router faqat ModelViewSet uchun
router = DefaultRouter()
router.register(r'users', UserViews, basename='users')

# 🔹 APIView larni oddiy path orqali ulaymiz
urlpatterns = [
    path('login/', AuthViews.as_view(), name='login'),
    path('students/import/', ImportStudents.as_view(), name='import-students'),
    path('reset-password/', ChangePasswordView.as_view(), name='user-reset-password'),
    path("my-students/",TeacherView.as_view(),name="my-students"),
    # router url-larni qo‘shamiz
    path('', include(router.urls)),
]

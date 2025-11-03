from django.urls import path
from rest_framework.routers import DefaultRouter
from school.views import ClassView, GradeView

router = DefaultRouter()

router.register('classes',ClassView,basename="class")
router.register('grade', GradeView, basename='grade')


urlpatterns = router.urls

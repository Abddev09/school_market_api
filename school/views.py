from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from user.models import User
from .models import Classe, Grade
from .serializers import (
    ClassSerializer, GradeSerializer
)
from .permission import GradePermission, ClassPermission




# --------------------------- Class CRUD ---------------------------
class ClassView(ModelViewSet):
    permission_classes = [ClassPermission]
    queryset = Classe.objects.all()
    serializer_class = ClassSerializer
    
    def perform_create(self, serializer):
        data = self.request.data
        teacher_id = data.get("teacher")
        teacher = User.objects.filter(id=teacher_id).first()
        serializer.save(
            teacher=teacher
        )


class GradeView(ModelViewSet):
    queryset = Grade.objects.all().select_related("student")
    serializer_class = GradeSerializer
    permission_classes = [GradePermission]

from rest_framework import serializers
from user.models import User
from user.serializer import UserSerializer
from .models import Classe, Grade

class GradeSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=True
    )
    student_detail = UserSerializer(read_only=True, source="student")

    class Meta:
        model = Grade
        fields = "__all__"

    def validate_ball(self, value):
        if value > 10:
            raise serializers.ValidationError("Ball 10 dan katta bo‘lishi mumkin emas.")
        if value < 0:
            raise serializers.ValidationError("Ball manfiy bo‘lishi mumkin emas.")
        return value

    def validate_student(self, value):
        if value is None:
            raise serializers.ValidationError("Student kiritilishi shart.")
        return value

# --------------------------- Class Serializer ---------------------------
class ClassSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=2),  # faqat o‘qituvchilarni tanlash
        required=False,
        allow_null=True,
    )
    teacher_detail = UserSerializer(read_only=True, source="teacher")

    class Meta:
        model = Classe
        fields = "__all__"
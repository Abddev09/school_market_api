from rest_framework import serializers
from user.models import User
from school.models import Classe


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    classe = serializers.SerializerMethodField(read_only=True)
    classe_id = serializers.PrimaryKeyRelatedField(
        queryset=Classe.objects.all(), source="classe", write_only=True, required=False
    )

    class Meta:
        model = User
        exclude = ["groups", "user_permissions"]
        read_only_fields = ["username", "created", "updated"]

    def get_classe(self, obj):
        if obj.classe:
            return {
                "id": obj.classe.id,
                "name": obj.classe.name,
            }
        return None

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        classe = validated_data.pop("classe", None)

        user = User.objects.create_user(password=password, **validated_data)

        if classe:
            user.classe = classe

        user.save()
        return user

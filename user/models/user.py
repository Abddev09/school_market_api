import random
import string
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.contrib.auth.hashers import make_password, is_password_usable

from school.models import Classe


class CustomUserManager(BaseUserManager):
    def generate_unique_username(self, first_name, last_name):
        first_name = (first_name or "").strip().lower()
        last_name = (last_name or "").strip().lower()

        if not first_name and not last_name:
            first_name = "user"

        patterns = [
            f"{first_name}{last_name}",
            f"{first_name}.{last_name}",
            f"{first_name}{last_name[:1]}",
            f"{first_name[:1]}.{last_name}",
            f"{first_name}.{last_name[:1]}",
        ]

        while True:
            pattern = random.choice(patterns) or "user"
            if random.choice([True, False]):
                random_num = ''.join(random.choices(string.digits, k=4))
                username = f"{pattern}{random_num}"
            else:
                username = pattern

            if username and not self.model.objects.filter(username=username).exists():
                return username

    def create_user(self, username=None, password=None, **extra_fields):
        first_name = extra_fields.get("first_name", "")
        last_name = extra_fields.get("last_name", "")

        if not first_name:
            raise ValueError("Foydalanuvchi uchun first_name kiritilishi shart!")

        if not username:
            username = self.generate_unique_username(first_name, last_name)
        extra_fields["username"] = username

        user = self.model(**extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(password=password, **extra_fields)

    def sudents(self):
        self.get_queryset().filter(role=3)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    username = models.CharField(max_length=255, unique=True, editable=False)
    ball = models.PositiveIntegerField(default=0)
    gender = models.BooleanField(default=True, choices=[
        (True, "Erkak 👨‍"),
        (False, "Ayol 🙍‍"),
    ])
    classe = models.ForeignKey(Classe,on_delete=models.SET_NULL,null=True,blank=True, related_name="students")
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    role = models.SmallIntegerField(
        verbose_name="User Type",
        default=3,
        choices=[
            (0, "Super Admin"),
            (1, 'Admin'),
            (2, "Teacher"),
            (3, "Student"),
        ]
    )

    created = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated = models.DateTimeField(auto_now=True, null=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.__class__.objects.generate_unique_username(
                self.first_name, self.last_name
            )

        # Parolni hash qilish
        if self.password and not is_password_usable(self.password):
            self.password = make_password(self.password)

        super().save(*args, **kwargs)


    class Meta:
        verbose_name_plural = "1. Users"

    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    def __str__(self):
        return self.username or self.full_name()


    def response(self):
        return {

        }




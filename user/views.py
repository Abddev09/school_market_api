import os
import random
import string
from methodism.helper import dictfetchall, dictfetchone 


from contextlib import closing

from django.db import connection


import pandas as pd

from openpyxl.utils import get_column_letter
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from school.models import Classe
from user.models import User
from user.serializer import UserSerializer
from utils.c_response import custom_response


# ------------------- AUTH LOGIN VIEW -------------------
class AuthViews(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer  # Faqat response uchun

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return custom_response(False, "Username va password kiritilishi shart", {}, 400)

        user = authenticate(username=username, password=password)
        if not user:
            return custom_response(False, "Noto‘g‘ri username yoki password", {}, 401)

        refresh = RefreshToken.for_user(user)
        data = {
            "user": UserSerializer(user).data,
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
        }
        return custom_response(True, "Tizimga kirildi", data, 200)


# ------------------- USER CRUD + ROLE LOGIC -------------------
class UserViews(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class StudentUserViews(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get(self, request, *args, **kwargs):
        students = User.objects.filter(role=3).order_by('-ball')
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)
    

class StudentPagination(PageNumberPagination):
    page_size = 40
    page_size_query_param = 'page_size'  # optional, foydalanuvchi o'zgartirishi mumkin
    max_page_size = 100

class StudentUserViewss(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StudentPagination

    def get(self, request, *args, **kwargs):
        class_id = request.query_params.get("class_id", None)  # query paramdan olish
        students = User.objects.filter(role=3).order_by('-ball')

        # Agar class_id berilgan bo‘lsa, filter qilish
        if class_id is not None:
            try:
                class_id_int = int(class_id)
                if class_id_int != 0:
                    students = students.filter(classe_id=class_id_int)
            except ValueError:
                pass

        page = self.paginate_queryset(students)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Fallback: pagination ishlamasa
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)
    
    
class TeacherUserViews(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get(self, request, *args, **kwargs):
        students = User.objects.filter(role=2)
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)


class TeacherView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        current_teacher = request.user
        with closing(connection.cursor()) as cursor:
            sql = f"""
            SELECT 
        uu.id AS student_id,
        uu.first_name,
        uu.last_name,
        uu.username,
        uu.gender,
        uu.classe_id,
        uu.ball,
        cls.id AS classe_id,
        cls.name AS classe_name,
        cls.teacher_id
    FROM user_user AS uu
    INNER JOIN school_classe AS cls ON cls.id = uu.classe_id
    WHERE uu.role = 3 AND cls.teacher_id = {request.user.id}
            """
            cursor.execute(sql)
            result = dictfetchall(cursor)

        return Response(result)

# ------------------- IMPORT STUDENT + EXEL FILE -----------------
class ImportStudents(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, FormParser]  # file upload uchun

    def post(self, request):
        current_user = request.user
        file = request.FILES.get('file')

        if not file:
            return custom_response(False, "Fayl yuborilmagan", {}, 400)

        # --- Ruxsatni tekshirish ---
        if current_user.role == 3:
            return custom_response(False, "Student foydalanuvchi import qila olmaydi", {}, 403)

        try:
            # Excel yoki CSV o‘qish
            if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                df = pd.read_excel(file)
            elif file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                return custom_response(False, "Faqat .xlsx yoki .csv fayllar qabul qilinadi", {}, 400)

            created_users = []
            for _, row in df.iterrows():
                first_name = str(row.get('first_name', '')).strip()
                last_name = str(row.get('last_name', '')).strip()
                gender = row.get('gender', True)
                password = str(row.get('password', '123456')).strip()  # default password

                classe_name = row.get('classe', None)

                if classe_name:
                    classe_obj, _ = Classe.objects.get_or_create(name=classe_name)
                    classe_obj.teacher = current_user
                    classe_obj.save()
                else:
                    classe_obj = None  # Agar faylda sinf ko‘rsatilmagan bo‘lsa

 
                user = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    classe=classe_obj,
                    role=3,              
                    is_staff=False,
                    password=password
                )

                # --- Student Profile yaratish ---

                created_users.append(UserSerializer(user).data)

            return custom_response(True, f"{len(created_users)} ta student muvaffaqiyatli import qilindi", created_users, 201)

        except Exception as e:
            return custom_response(False, f"Xatolik yuz berdi: {str(e)}", {}, 500)




class ChangePasswordView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user_id = request.data.get("id")
        new_password = request.data.get("new_password")

        if not user_id or not new_password:
            return custom_response(False, "ID va yangi parol kiritilishi shart", {}, 400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return custom_response(False, "Bunday foydalanuvchi topilmadi", {}, 404)

        user.set_password(new_password)
        user.save()

        return custom_response(True, "Parol muvaffaqiyatli o‘zgartirildi", {"username": user.username}, 200)


def generate_7_digit_password():
    """7 xonali raqamiy vaqtinchalik parol (string)"""
    return ''.join(random.choices(string.digits, k=7))


def autosize_columns(ws, dataframe, min_width=10, max_width=50):
    """
    Simple column width adjuster: hisoblab chiqadi va o'rnatadi.
    Pandas->Excel orqali yozilgandan keyin ishlatiladi.
    """
    for i, col in enumerate(dataframe.columns, 1):
        max_len = max(
            dataframe[col].astype(str).map(len).max() if not dataframe.empty else 0,
            len(str(col))
        ) + 2
        max_len = max(min_width, min(max_len, max_width))
        ws.column_dimensions[get_column_letter(i)].width = max_len

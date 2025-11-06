import os
import random
import string
from datetime import datetime
from methodism.helper import dictfetchall, dictfetchone 


from contextlib import closing

from django.db import connection


import pandas as pd
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from openpyxl import load_workbook
from openpyxl.styles import Alignment, PatternFill, Font, Side, Border
from openpyxl.utils import get_column_letter

from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from school.models import Classe
from school.serializers import ClassSerializer
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


class TeacherView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        current_teacher = request.user

        # O'qituvchining sinfini topamiz
        # classe = Classe.objects.filter(teacher=current_teacher).first()
        # if not classe:
        #     return Response({"detail": "Sizga birorta sinf biriktirilmagan."}, status=404)

        # # Shu sinfdagi o'quvchilarni olamiz
        # students = User.objects.sudents.filter(Q(classe__teacher=request.User))

        # serializer = self.get_serializer(students, many=True)
        # classe_seri = ClassSerializer(classe)
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
                classe = row.get('classe',None)
                password = str(row.get('password', '123456')).strip()  # default password

                classe, _ = Classe.objects.get_or_create(name=classe)

                if not first_name:
                    continue  # ism bo‘lmasa o‘tkazib yuboramiz

                # --- Student yaratish ---
                user = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    classe=classe,
                    role=3,              # har doim student
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


class ExportUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        POST body:
        {
          "role": "teacher" | "student"
        }

        Response (success):
        {
          "success": True,
          "message": "...",
          "file_path": "<MEDIA_URL>/teachers_20251027_120000.xlsx"
        }
        """
        try:
            role = (request.data.get("role") or "").strip().lower()
            if role not in ["teacher", "student"]:
                return custom_response(False, "Role noto‘g‘ri kiritildi", {}, 400)

            # role -> numeric mapping
            role_map = {"teacher": 2, "student": 3}
            role_num = role_map[role]

            # Queryset: select fields we need
            qs = User.objects.filter(role=role_num).values(
                "id", "username", "first_name", "last_name", "classe__name"
            )

            if not qs.exists():
                return custom_response(False, f"{role.title()}lar topilmadi", {}, 404)

            rows = []
            # We will collect rows and also update passwords inside a transaction
            now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{role}s_{now_str}.xlsx"
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)

            with transaction.atomic():
                for u in qs:
                    temp_pw = generate_7_digit_password()
                    # update DB: hash password and save
                    User.objects.filter(id=u["id"]).update()  # ensure object exists
                    user_obj = User.objects.get(id=u["id"])
                    user_obj.set_password(temp_pw)
                    user_obj.save(update_fields=["password"])

                    rows.append({
                        "id": u["id"],
                        "class":u["class"],
                        "username": u["username"],
                        "first_name": u.get("first_name", ""),
                        "last_name": u.get("last_name", ""),
                        "temp_password": temp_pw,   # plaintext only for Excel
                    })

            # Create DataFrame
            df = pd.DataFrame(rows, columns=[
                "id", "username", "first_name", "last_name","temp_password"
            ])

            # Write to Excel via pandas (openpyxl engine)
            # Ensure media folder exists
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name=role.title())

            # Open workbook with openpyxl and apply styling
            wb = load_workbook(file_path)
            ws = wb[role.title()]

            # Header styling: bold, white font on colored fill
            header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=12)
            center_align = Alignment(vertical="center", horizontal="center", wrap_text=True)
            thin = Side(border_style="thin", color="000000")
            border = Border(left=thin, right=thin, top=thin, bottom=thin)

            # Apply header styles
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = center_align
                cell.border = border

            # Apply alternating row fill (zebra)
            fill_gray = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
            for idx, row in enumerate(ws.iter_rows(min_row=2, max_row=ws.max_row), start=2):
                if idx % 2 == 0:
                    for cell in row:
                        cell.fill = fill_gray
                for cell in row:
                    cell.alignment = Alignment(vertical="center", horizontal="left", wrap_text=True)
                    cell.border = border

            # Autosize columns based on dataframe content
            autosize_columns(ws, df)

            # Freeze header row
            ws.freeze_panes = ws["A2"]

            # Save workbook (overwrite)
            wb.save(file_path)

            # Return MEDIA_URL path (ensure MEDIA_URL ends with '/')
            media_url = settings.MEDIA_URL if settings.MEDIA_URL.endswith("/") else settings.MEDIA_URL + "/"
            public_path = os.path.join(media_url, file_name)

            return custom_response(True, f"{role.title()}lar fayli tayyor", {"file_path": public_path}, 200)

        except Exception as e:
            return custom_response(False, f"Xatolik yuz berdi: {str(e)}", {}, 500)
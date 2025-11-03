import random
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import User

@receiver(post_migrate)
def create_default_users(sender, **kwargs):
    # faqat user app uchun ishlasin
    if sender.name != "user":
        return

    # ✅ SUPERUSER (role=0)
    if not User.objects.filter(username="school255").exists():
        User.objects.create(
            username="immortal_admin",
            password="atomic",
            first_name=random.choice(["Ali", "Jasur", "Bekzod", "Aziz"]),
            last_name=random.choice(["Qodirov", "Aliyev", "Tursunov", "Rustamov"]),
            role=0,
            is_superuser=True,
            is_staff=True,
        )
        print("✅ Superuser 'immortal_admin' created with password 'atomic'")

    # ✅ ADMIN (role=1)
    if not User.objects.filter(username="admin255").exists():
        User.objects.create(
            username="school255",
            password="255school",
            first_name=random.choice(["Dilshod", "Kamol", "Shuhrat", "Sardor"]),
            last_name=random.choice(["Abdullaev", "Karimov", "Rahimov", "Soliev"]),
            role=1,
            is_staff=True,
        )
        print("✅ Admin 'school255' created with password '255school'")

import datetime
import random

from django.db import models

def default_receipt_date():
    return datetime.datetime(2026, 5, 25, 9, 0)

def random_id():
    return random.randint(10_000_000, 99_999_999)


class Order(models.Model):
    student = models.ForeignKey('user.User',on_delete=models.CASCADE,related_name="orders")
    product = models.ForeignKey('market.Product',on_delete=models.SET_NULL,null=True,related_name="orders")
    date = models.DateTimeField(auto_now_add=True)
    receipt_date = models.DateTimeField(default=default_receipt_date)
    code = models.CharField(default=random_id)
    status = models.CharField(
        max_length=20,
        choices=(
            ("1", "Kutishda"),
            ("2", "Yakunlandi"),
        ),
        default="1",
    )


    def __str__(self):
        return f"{self.student.first_name}"

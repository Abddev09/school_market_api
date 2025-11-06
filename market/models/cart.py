from django.db import models


class Cart(models.Model):
    product = models.ForeignKey('market.Product',on_delete=models.DO_NOTHING,null=True)
    student = models.ForeignKey('user.User',on_delete=models.SET_NULL,null=True,related_name="cart")

    def __str__(self):
        return self.student.username
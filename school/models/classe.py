from django.db import models


class Classe(models.Model):
    name = models.CharField(max_length=40)
    teacher = models.ForeignKey('user.User',on_delete=models.SET_NULL,null=True,related_name="classes_as_teacher")

    def __str__(self):
        return self.name
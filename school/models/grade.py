from django.db import models


class Grade(models.Model):
    student = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True, related_name="grades")
    ball = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        # avval o‘zi saqlansin (Grade yaratiladi yoki update qilinadi)
        is_new = self.pk is None  # yangi yaratilayotganini aniqlaymiz
        super().save(*args, **kwargs)

        # agar yangi baho bo‘lsa, studentga ball qo‘shamiz
        if is_new and self.student:
            self.student.ball += self.ball
            self.student.save()

    def __str__(self):
        return f"{self.student.first_name} - {self.ball}"

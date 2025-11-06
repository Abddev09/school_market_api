from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    desc = models.TextField()
    price = models.PositiveIntegerField(null=True,blank=True)
    count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to="products/",null=True,blank=True)


    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save()

    def __str__(self):
        return self.name
from django.contrib import admin

from market.models import  Product, Favourite, Cart, Order

# Register your models here.
admin.site.register(Product)
admin.site.register(Favourite)
admin.site.register(Cart)
admin.site.register(Order)
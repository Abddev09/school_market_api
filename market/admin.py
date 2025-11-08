from django.contrib import admin

from market.models import  Product, Favourite, Cart, Order

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active')

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.hard_delete()

admin.site.register(Favourite)
admin.site.register(Cart)
admin.site.register(Order)
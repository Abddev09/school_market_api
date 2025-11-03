from rest_framework import serializers
from .models import Product,  Cart, Favourite, Order



# --------------------------------- Product Serializer ------------------------------
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


# --------------------------------- Cart Serializer ------------------------------
class CartSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True
    )
    product_detail = ProductSerializer(read_only=True, source="product")

    student = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Cart
        fields = "__all__"


# --------------------------------- Favourite Serializer ------------------------------
class FavouriteSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True
    )
    product_detail = ProductSerializer(read_only=True, source="product")

    student = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Favourite
        fields = "__all__"


# --------------------------------- Order Serializer ------------------------------
class OrderSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True
    )
    product_detail = ProductSerializer(read_only=True, source="product")
    student = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = "__all__"

    def validate(self, attrs):
        request = self.context.get("request")
        student = request.user  # foydalanuvchi (student)
        product = attrs.get("product")

        # 🧠 1. Talabaning balli mahsulot narxidan kam bo‘lsa — xatolik
        if student.ball < product.price:
            raise serializers.ValidationError({
                "detail": f"Sizda {student.ball} ta ball bor, ammo bu mahsulot uchun {product.price} ball kerak."
            })

        # 🧠 2. Product count yetarli bo‘lmasa
        if product.count <= 0:
            raise serializers.ValidationError({
                "detail": "Bu mahsulot hozirda mavjud emas."
            })

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        student = request.user
        product = validated_data.get("product")

        # 🧾 Xarid qilish
        order = Order.objects.create(
            student=student,
            product=product,
            status=1  # masalan, 'Kutishda' holati
        )

        # 🔻 Studentning ballidan mahsulot ballini ayiramiz
        student.ball -= product.price
        student.save()

        # 🔻 Product count dan 1 ni kamaytiramiz
        product.count -= 1
        product.save()

        return order


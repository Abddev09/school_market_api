from django.template.context_processors import request
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from market.models import Favourite, Order, Cart, Product
from market.serializers import (
    OrderSerializer, FavouriteSerializer, CartSerializer,
    ProductSerializer
)



# --------------------------- Product CRUD ---------------------------
class ProductView(ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer





# --------------------------- Favourite CRUD ---------------------------
class FavouriteView(ModelViewSet):
    serializer_class = FavouriteSerializer

    def get_queryset(self):
        user = self.request.user
        # Faqat shu userning sevimlilari chiqadi
        return Favourite.objects.filter(student=user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


# --------------------------- Order CRUD ---------------------------
class OrderView(ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user

        # Agar user role 1 (admin) yoki 0 (operator) bo‘lsa — hamma orderlarni ko‘rsatamiz
        if user.role in [0, 1]:
            return Order.objects.all()

        # Aks holda — faqat o‘z buyurtmalarini
        return Order.objects.filter(student=user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


# --------------------------- Cart CRUD ---------------------------
class CartView(ModelViewSet):
    serializer_class = CartSerializer

    def get_queryset(self):
        user = self.request.user
        # Faqat shu userning savatchasi chiqadi
        return Cart.objects.filter(student=user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)






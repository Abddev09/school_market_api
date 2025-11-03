from rest_framework.routers import DefaultRouter

from market.views import  ProductView, OrderView, CartView, FavouriteView

router = DefaultRouter()
router.register(r"products", ProductView, basename="products")
router.register(r"orders", OrderView, basename="orders")
router.register(r"carts", CartView, basename="carts")
router.register(r"favourite", FavouriteView, basename="favourite")

urlpatterns = router.urls

from rest_framework_nested import routers

from .views import *

router = routers.DefaultRouter()
router.register('products', ProductViewSet)
router.register('customers', CustomerViewSet)
router.register('carts', CartViewSet)
router.register('orders', OrderViewSet, basename='order')

review = routers.NestedDefaultRouter(router, 'products', lookup='product')
review.register('reviews', ReviewViewSet, basename='reviews')

cart_item = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_item.register('items', CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + review.urls + cart_item.urls
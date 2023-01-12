from django.urls import path
from rest_framework_nested import routers
from .views import *
# urlpatterns = [
#     path('products/', ProductList2.as_view()),
#     path('products/<int:pk>/', ProductDetail2.as_view()),
#     path('collections/', CollectionList.as_view()),
#     path('collections/<int:pk>', CollectionDetail.as_view(), name='collection-detail')
# ]

router = routers.DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('collections', CollectionViewSet, basename='collection')
router.register('carts', CartViewSet)
router.register('customer', CustomerViewSet, basename='customer')
router.register('orders', OrderViewSet, basename='order')

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', ReviewViewSet, basename='product-reviews')
items_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
items_router.register('items', ItemViewSet, basename='item')

urlpatterns = router.urls + products_router.urls + items_router.urls
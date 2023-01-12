from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import permissions

from django_filters.rest_framework import DjangoFilterBackend

from .models import *
from .serializers import *
from .filters import ProductFilter
from .permissions import IsAdminOrReadOnly, OrderPermission


# Create your views here.

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related('collection').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    # search_fields = ['collection__title']
    search_fields = ['^title']
    ordering_fields = ['unit_price']
    permission_classes = [IsAdminOrReadOnly]

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(product__id=self.kwargs['product_pk']).filter(is_show=True).select_related('user')

    def get_serializer_context(self):
        context = super(ReviewViewSet, self).get_serializer_context()
        context['user'] = self.request.user
        context['product_id'] = self.kwargs['product_pk']
        return context


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False)
    def me(self, request):
        customer = Customer.objects.get(user=self.request.user)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super(CustomerViewSet, self).get_serializer_context()
        context['user_id'] = self.request.user.id
        return context


class CartViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):

    queryset = Cart.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateCartSerializer
        else:
            return CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk'])

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CartItemSerializer
        elif self.request.method == 'POST':
            return PostCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer

    def get_serializer_context(self):
        context = super(CartItemViewSet, self).get_serializer_context()
        context['cart_id'] = self.kwargs['cart_pk']
        return context

class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch']
    # permission_classes = [OrderPermission]

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [OrderPermission()]
        else:
            return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrderSerializer
        elif self.request.method == 'PATCH':
            return CancelOrderSerializer
        return ShowOrderSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer__user=self.request.user).all()

    def get_serializer_context(self):
        context = super(OrderViewSet, self).get_serializer_context()
        context['user_id'] = self.request.user.id
        return context

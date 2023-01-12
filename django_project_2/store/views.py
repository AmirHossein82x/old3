from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, DjangoModelPermissions
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Product, Collection, Review, OrderItem, Cart, CartItem, Customer, Order
from .permissions import IsAdminOrReadOnly, FullModelDjangoPermissions, ViewCustomerHistoryPermission
from .serializers import ProductSerializer, CollectionSerializer, CollectionSerializer2, ReviewSerializer, \
    CartSerializer, ItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer, CustomerSerializer, \
    OrderSerializer, OrderItemSerializer, CreateOrderSerializer, UpdateOrderSerializer
from .pagination import DefaultPagination
from .filters import ProductFilter



from rest_framework.mixins import CreateModelMixin
# Create your views here.
@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        query_set = Product.objects.select_related('collection').all()
        serializer = ProductSerializer(query_set, many=True, context={'request': request})
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        # if serializer.is_valid():    way 1
        #     serializer.validated_data
        #     return Response('ok')
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.is_valid(raise_exception=True)     # way 2
        print(serializer.validated_data)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])     # PUT: for updating all properties   PATCH: for updating subset of properties
def product_detail(request, pk):

    """way 1"""
    # try:
    #     product = Product.objects.get(pk=id)
    #     serializer = ProductSerializer(product)
    #     return Response(serializer.data)
    # except Product.DoesNotExist:
    #     # return Response(status=404)  way 1
    #     return Response(status=status.HTTP_404_NOT_FOUND)

    # way 2
    product = get_object_or_404(Product, pk=pk)
    if request.method == "GET":
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if product.orderitems.count() > 0:
            return Response({"error": "product can not be deleted"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def collection_list(request):
    if request.method == 'GET':
        query_set = Collection.objects.annotate(products_count=Count('product'))
        serializer = CollectionSerializer2(query_set, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = CollectionSerializer2(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CollectionList(ListCreateAPIView):
    queryset = Collection.objects.annotate(products_count=Count('product'))
    serializer_class = CollectionSerializer2


@api_view(['GET', "PUT", "DELETE"])
def collection_detail(request, pk):
    collection = get_object_or_404(Collection.objects.annotate(products_count=Count('product')), pk=pk)
    if request.method == 'GET':
        serializer = CollectionSerializer2(collection)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = CollectionSerializer2(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if collection.product_set.count() > 0:
            return Response({'error': 'this collection can not be deleted'})
        else:
            collection.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

class CollectionDetail(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.annotate(products_count=Count('product'))
    serializer_class = CollectionSerializer2

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.product_set.count() > 0:
            return Response({"error": 'you can not delete this collection because it is associated with product'})
        else:
            collection.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)



class ProductList(APIView):
    def get(self, request):
        query_set = Product.objects.select_related('collection').all()
        serializer = ProductSerializer(query_set, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # way 2
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProductList2(ListCreateAPIView):
    queryset = Product.objects.select_related('collection').all()
    serializer_class = ProductSerializer

    # def get_queryset(self):
    #     return Product.objects.select_related('collection').all()
    #
    # def get_serializer_class(self):
    #     return ProductSerializer

    def get_serializer_context(self):
        return {'request': self.request}

class ProductDetail(APIView):

    def get(self, request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, id):
        product = get_object_or_404(Product, pk=id)
        if product.orderitems.count() > 0:
            return Response({"error": "product can not be deleted"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class ProductDetail2(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # lookup_field = 'id'    # if we use this method we can use id instead of pk in the url

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=id)
        if product.orderitems.count() > 0:
            return Response({"error": "product can not be deleted"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['collection_id']  # if we want to filter simple
    filterset_class = ProductFilter
    search_fields = ['title', 'description']  # we can use collection__title
    ordering_fields = ['unit_price', 'last_update']
    permission_classes = [IsAdminOrReadOnly]

    # pagination_class = PageNumberPagination
    pagination_class = DefaultPagination

    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     # collection_id = self.request.query_params['collection_id']  # if we do not pass the collection_id to url it raise error
    #     collection_id = self.request.query_params.get('collection_id')  # if collection_id is not enterd in the url it will return None
    #     if collection_id is not None:
    #         queryset = queryset.filter(collection_id=collection_id)
    #     return queryset

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).exists():
            return Response({'error': 'you can not delete this product'})
        else:
            return super(ProductViewSet, self).destroy(request, *args, **kwargs)

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('product'))
    serializer_class = CollectionSerializer2
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).exists():
            return Response({'error': 'you can not delete this product'})
        else:
            return super(CollectionViewSet, self).destroy(request, *args, **kwargs)

class ReviewViewSet(ModelViewSet):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        context = super(ReviewViewSet, self).get_serializer_context()
        context['product_id'] = self.kwargs['product_pk']
        return context

# class CartViewSet(CreateModelMixin, GenericViewSet):
class CartViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet
                  ):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer

class ItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']  # these must be lower case

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        else:
            return ItemSerializer

    def get_queryset(self):
        # return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).prefetch_related('product')
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')

    def get_serializer_context(self):
        context = super(ItemViewSet, self).get_serializer_context()
        context['cart_id'] = self.kwargs['cart_pk']
        # context['item_pk'] = self.kwargs['pk']
        return context

class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]        # we can use permission_classes in the action decorator too
    # permission_classes = [DjangoModelPermissions]
    # permission_classes = [FullModelDjangoPermissions]
    # def get_permissions(self):
    #     if self.request.method == "GET":
    #         return [AllowAny()]
    #     else:
    #         return [IsAuthenticated()]

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])    # if we use False the url is like this  http://127.0.0.1:8000/store/customer/me   # if we use True this action is avalable in detail view  http://127.0.0.1:8000/store/customer/1/me
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            customer_serializer = CustomerSerializer(customer)
            return Response(customer_serializer.data)
        elif request.method == 'PUT':
            customer_serializer = CustomerSerializer(customer, data=request.data)
            customer_serializer.is_valid(raise_exception=True)
            customer_serializer.save()
            return Response(customer_serializer.data)

    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):
        return Response('ok')

class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'delete', 'patch', 'head', 'options', 'post']
    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()

        user_id = self.request.user.id
        customer_id = Customer.objects.only('id').get(user_id=user_id)
        return Order.objects.filter(customer_id=customer_id)

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer


    # def get_serializer_context(self):     we use this when we do not want to override the create mehthod in the ModelMixin
    #     context = super(OrderViewSet, self).get_serializer_context()
    #     context['user_id'] = self.request.user.id
    #     return context

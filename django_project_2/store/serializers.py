from django.db import transaction
from rest_framework import serializers
from decimal import Decimal
from .models import Product, Collection, Review, Cart, CartItem, Customer, Order, OrderItem
from .singnals import order_created


# class CollectionSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)

# class ProductSerializer(serializers.Serializer):        way 1
# id = serializers.IntegerField()
# title = serializers.CharField(max_length=255)
# price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')
# price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
# # collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all())  way 1
# # collection = serializers.StringRelatedField()  way 2
# # collection = CollectionSerializer()       way 3
# collection = serializers.HyperlinkedRelatedField(
#     queryset=Collection.objects.all(),
#     view_name='collection-detail'
# )

# def calculate_tax(self, product):
#     return product.unit_price * Decimal(1.1)

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title']
    # products_count = serializers.IntegerField()

    # def products2_count(self, collection):
    #     return collection.product_set

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'price', 'price_with_tax', 'collection']

    collection = serializers.HyperlinkedRelatedField(
        queryset=Collection.objects.all(),
        view_name='collection-detail'
    )
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')

    def calculate_tax(self, product):
        return product.unit_price * Decimal(1.1)

    # we can override the validate method
    # this is just a test, we do not use it in this project yet
    # def validate(self, attrs):
    #     if attrs['password'] != attrs['confrim_password']:
    #         raise serializers.ValidationError('password and confirm are not match')
    #     return attrs

    # we can override create and add some value we want
    # def create(self, validated_data):
    #     product = Product(**validated_data)
    #     product.title = "hassan"
    #     product.unit_price = 20
    #     product.save()
    #     return product
    #
    # def update(self, instance, validated_data):
    #     instance.unit_price = validated_data.get('unit_price')
    #     instance.save()
    #     return instance

class CollectionSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    """this way ends up with lots of query"""
    # products = serializers.SerializerMethodField(method_name='product_count')
    #
    # def product_count(self, collection):
    #     return collection.product_set.count()

    products_count = serializers.IntegerField(read_only=True)

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user', 'text']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart: Cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])


    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']

class ItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, item):
        return item.quantity * item.product.unit_price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('no product with the given id was found')
        return value


    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(cart__id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

    # def save(self, **kwargs):    # it works without this function too
    #     cart_item = CartItem.objects.get(pk=self.context['item_pk'])
    #     cart_item.quantity = self.validated_data['quantity']
    #     cart_item.save()
    #     self.instance = cart_item
    #     return self.instance


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']

class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items']

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('there is no cart with the given id')

        elif not CartItem.objects.filter(cart_id=cart_id).exists():
            raise serializers.ValidationError({'error': 'you can not make order because this cart is empty'})
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            customer = Customer.objects.get(user_id=self.context.get('user_id'))
            order = Order.objects.create(customer=customer)
            cart_items = CartItem.objects.select_related('product').filter(cart__id=self.validated_data['cart_id'])
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                )
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk=self.validated_data['cart_id']).delete()
            order_created.send_robust(self.__class__, order=order)
            return order



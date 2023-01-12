from django.db import transaction
from rest_framework import serializers

from .models import *

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title']

class ProductSerializer(serializers.ModelSerializer):
    collection = CollectionSerializer()

    class Meta:
        model = Product
        fields = ['title', 'collection', 'description', 'unit_price']


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)

    def get_username(self, review):
        return review.user.username

    class Meta:
        model = Review
        fields = ['username', 'text', 'is_recommended']

    def save(self, **kwargs):
        product = Product.objects.get(pk=self.context['product_id'])
        Review.objects.create(
            user=self.context['user'],
            product=product,
            **self.validated_data
        )


class CustomerSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    def get_username(self, customer):
        return customer.user.username

    class Meta:
        model = Customer
        fields = ['username', 'membership']

    def save(self, **kwargs):
        if Customer.objects.get(user_id=self.context['user_id']):
            raise serializers.ValidationError('you already have profile')
        else:
            Customer.objects.create(user_id=self.context['user_id'], **self.validated_data)


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    price = serializers.SerializerMethodField()

    def get_price(self, cart_item):
        return cart_item.product.unit_price * cart_item.quantity

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'price']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class PostCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if Product.objects.filter(pk=value).exists():
            return value
        raise serializers.ValidationError('this product does not exist')

    class Meta:
        model = CartItem
        fields = ['product_id', 'quantity']

    def save(self, **kwargs):
        if not CartItem.objects.filter(product_id=self.validated_data['product_id']).exists():
            CartItem.objects.create(cart_id=self.context['cart_id'], **self.validated_data)
        else:
            cart_item = CartItem.objects.get(cart_id=self.context['cart_id'], product_id=self.validated_data['product_id'])
            cart_item.quantity += self.validated_data['quantity']
            cart_item.save()



class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum(item.product.unit_price * item.quantity for item in cart.items.all())

    class Meta:
        model = Cart
        fields = ['items', 'total_price']

class CreateCartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id']


class OrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('this cart_id does not exist')

        elif not Cart.objects.get(pk=cart_id).items.all().exists():
            raise serializers.ValidationError('this cart_id has no product')

        else:
            return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            customer = Customer.objects.get(user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer)
            cart_items = CartItem.objects.filter(cart_id=self.validated_data['cart_id'])
            order_items = [OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                total_price=item.product.unit_price * item.quantity
            )
                           for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk=self.validated_data['cart_id']).delete()

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'total_price']

class ShowOrderSerializer(serializers.ModelSerializer):
    customer_username = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True, read_only=True)

    def get_customer_username(self, value):
        return value.customer.user.username

    class Meta:
        model = Order
        fields = ['customer_username', 'items', 'status']


class CancelOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']
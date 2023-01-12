from django.core.validators import MinValueValidator
from django.conf import settings
from django.db import models

from uuid import uuid4

# Create your models here.

class Collection(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Promotion(models.Model):
    title = models.CharField(max_length=255)
    discount = models.DecimalField(decimal_places=1, max_digits=3)

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=255)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    slug = models.SlugField()
    description = models.TextField()
    inventory = models.PositiveIntegerField()
    promotion = models.ManyToManyField(Promotion)
    unit_price = models.DecimalField(decimal_places=3, max_digits=5)

    def __str__(self):
        return self.title


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_DEFAULT, default='deleted_user')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    is_show = models.BooleanField(default=False)
    is_recommended = models.BooleanField()

    def __str__(self):
        return f"{self.user} reviews on {self.product}"


class Customer(models.Model):
    MEMBERSHIP = [
        ('G', 'GOLD'),
        ('S', 'SILVER'),
        ('B', 'BRONZE')
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True)
    membership = models.CharField(max_length=1, choices=MEMBERSHIP, default='B')

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(membership__in=['G', 'S', 'B']),
                name='check membership',
                violation_error_message='The selected membership does not exist'
            )
        ]


class Address(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='address')
    city = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    description = models.TextField(blank=True)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])


class Order(models.Model):
    status_choices = [
        ('C', 'cancel'),
        ('a', 'active')
    ]
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=status_choices, max_length=1)

    class Meta:
        permissions = [
            ('can_cancel_order', 'can cancel order')
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total_price = models.DecimalField(decimal_places=3, max_digits=5)

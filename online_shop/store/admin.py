from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from django.shortcuts import reverse
from django.utils.http import urlencode

from .models import *


# Register your models here.

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'collection', 'unit_price', 'inventory', 'available']
    list_editable = ['inventory']
    list_filter = ['collection']
    inlines = [ReviewInline]
    autocomplete_fields = ['collection']
    prepopulated_fields = {'slug': ['title']}

    def available(self, product):
        return True if product.inventory > 0 else False


@admin.register(Collection)
class Collection(admin.ModelAdmin):
    list_display = ['id', 'title', 'product']
    search_fields = ['title__istartswith']
    ordering = ['id']

    def product(self, collection):
        url = (reverse('admin:store_product_changelist')
               + '?'
               + urlencode(
                    {
                        'collection__id__exact': str(collection.id)
                    }
                )
               )
        return format_html("<a href={}>{}</a>", url, collection.product_count)

    def get_queryset(self, request):
        return super(Collection, self).get_queryset(request).annotate(product_count=Count('product'))


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'created_at']
    inlines = [OrderItemInline]

    def email(self, order):
        return order.customer.user.email

    def get_queryset(self, request):
        return super(OrderAdmin, self).get_queryset(request).select_related('customer__user')


class MemberShipFilter(admin.SimpleListFilter):
    title = 'membership'
    parameter_name = 'membership'

    def lookups(self, request, model_admin):
        if Customer.objects.filter(membership='G').exists():
            yield 'G', 'Gold members'

        if Customer.objects.filter(membership='S').exists():
            yield 'S', 'Silver members'

        if Customer.objects.filter(membership='B').exists():
            yield 'B', 'Bronze members'

    def queryset(self, request, queryset):
        if self.value() == 'G':
            return queryset.filter(membership='G')

        if self.value() == 'S':
            return queryset.filter(membership='S')

        if self.value() == 'G':
            return queryset.filter(membership='S')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'membership']
    list_filter = [MemberShipFilter]

    def email(self, customer):
        return customer.user.email

    def get_queryset(self, request):
        return super(CustomerAdmin, self).get_queryset(request).select_related('user')

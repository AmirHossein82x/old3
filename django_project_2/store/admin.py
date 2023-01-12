from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html, urlencode
from django.urls import reverse
from django.db.models import Count, QuerySet
# from tags.models import TagItem

from .models import *


# Register your models here.

class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'  # this will show in the filter list
    parameter_name = 'inventory'  # this will show in the url

    def lookups(self, request, model_admin):
        return [
            ('<10', 'low')
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # inlines = [TagInline]
    # fields = ['title', 'description']  it will show in the panel admin where we want to add a new product
    # exclude = ['promotion']  it is the opposite of the above
    # readonly_fields = ['title']  we can just read it and we can not fill that field
    prepopulated_fields = {       # it will automaticly fill the slug with title
        'slug': ['title']
    }
    autocomplete_fields = ['collection']
    actions = ['clear_inventory']
    search_fields = ['title__istartswith']
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_per_page = 10
    list_select_related = ['collection']
    list_filter = ['collection', 'last_update', InventoryFilter]
    date_hierarchy = 'last_update'
    # fields = [('title', 'unit_price'), 'inventory', 'slug']  # title and unit_price will show in the same line
    # form = None   we can create a form and use it here that show in the  admin panel


    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'Ok'

    @admin.action(description='clear inventory')
    def clear_inventory(self, request, queryset: QuerySet):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f"{updated_count} products were successfully updated",
            messages.ERROR
        )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership']
    list_editable = ['membership']
    list_per_page = 10
    ordering = ['user__first_name', 'user__last_name']
    autocomplete_fields = ['user']
    search_fields = ['user__first_name__istartswith',
                     'user__last_name__istartswith']  # any one thier first_name or last_name startwith the letter that we enter

    def first_name(self, customer):
        return customer.user.first_name

    def last_name(self, customer):
        return customer.user.last_name

    def get_queryset(self, request):
        return super(CustomerAdmin, self).get_queryset(request).select_related('user')

class OrderItemInline(admin.TabularInline):  # admin.StackedInline
    model = OrderItem
    autocomplete_fields = ['product']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'placed_at', 'customer']
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields = ['title__istartswith']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        # url = reverse('admin:store_product_changelist') + '?' + f"{collection.id}"   we can not use this way
        url = (reverse('admin:store_product_changelist')
               + "?"
               + urlencode({
                    'collection__id': str(collection.id)
                }))
        return format_html("<a href='{}'>{}</a>", url, collection.products_count)

    def get_queryset(self, request):
        return super(CollectionAdmin, self).get_queryset(request).annotate(products_count=Count('product'))
# admin.site.register(Product)

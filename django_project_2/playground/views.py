from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.aggregates import Count, Max, Min, Avg
from django.db import transaction
from django.db.models import Value, Func
from django.db.models import Q, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Concat
from store.models import Product
from store.models import Customer
from store.models import Collection
from store.models import Order, OrderItem
from django.db import connection

from django.contrib.contenttypes.models import ContentType
from tags.models import TagItem


# Create your views here.
# @transaction.atomic  it will wrap all the function in to one transaction
def say_hello(request):
    query_set = Product.objects.all()  # it gives all the products
    product = Product.objects.get(pk=1)  # it gives one product with id 1
    # way 1
    # try:
    #     product = Product.objects.get(pk=0)
    # except ObjectDoesNotExist:
    #     print('not found')
    # way 2
    product = Product.objects.filter(pk=0).first()  # it returns None
    exists = Product.objects.filter(pk=0).exists()  # it returns True or False
    product = Product.objects.get(id__exact=4)
    """
    go to django project in the section field lookups
    """
    query_set = Product.objects.filter(unit_price__gt=20)  # it returns all the product which unit_price more than 20
    query_set = Product.objects.filter(unit_price__range=(20, 30))  # it returns all the product which unit_price more than 20 and less than 30
    query_set = Product.objects.filter(title__contains='coffee')  # it returns products which there is coffee in their title ## this is case sensitive
    query_set = Product.objects.filter(title__icontains='coffee')  # it is just like the above line just incase sensitive
    query_set = Product.objects.filter(title__startswith='coffee')
    query_set = Product.objects.filter(title__istartswith='coffee')
    query_set = Product.objects.filter(last_update__year=2021)
    query_set = Product.objects.filter(description__isnull=True)
    query_set = Customer.objects.filter(email__icontains='.com')
    query_set = Collection.objects.filter(featured_product__isnull=True)
    query_set = Product.objects.filter(inventory__lt=10)
    query_set = Order.objects.filter(customer_id=1)
    customer_id = [order.id for order in query_set]
    query_set1 = Customer.objects.filter(id__in=customer_id)  # wrong
    query_set2 = Customer.objects.filter(order__customer_id=1).distinct()
    query_set = OrderItem.objects.filter(product__collection_id=3)
    # print(query_set.explain())

    # products with inventory < 10 and price < 20
    # way 1
    query_set = Product.objects.filter(inventory__lt=10, unit_price__lt=20)
    # way 2
    query_set = Product.objects.filter(inventory__lt=10).filter(unit_price__lt=20)
    # way 3
    query_set = Product.objects.filter(Q(inventory__lt=10) & Q(unit_price__lt=20))  # this way is not common

    # products with inventory < 10 or price < 20
    query_set = Product.objects.filter(Q(inventory__lt=10) | Q(unit_price__lt=20))

    # note  ~ is NOT in sql
    query_set = Product.objects.filter(Q(inventory__lt=10) & ~Q(unit_price__lt=20))  # returns inventory more than 10 and unit_price GRATER THAN 20

    # if we want to compare 2 fields we use F
    query_set = Product.objects.filter(inventory=F('unit_price'))
    query_set = Product.objects.filter(inventory=F('collection__title'))
    query_set = Product.objects.order_by('unit_price', '-title')
    query_set = Product.objects.order_by('unit_price', '-title').reverse()
    query_set = Product.objects.order_by('unit_price')[0:5]

    product = Product.objects.earliest('unit_price')  # it returns one object
    product = Product.objects.latest('unit_price')  # it returns one object
    query_set = Product.objects.values('id', 'title')  # it returns a dictionary
    query_set2 = Product.objects.only('id', 'title')  # it returns an object and if we want to select a field that is not in the only clause it takes several seconds
    query_set2 = Product.objects.defer('description')  # it is just like above and returns all fiedld except description and if we select description in the remplate it will takes several second
    query_set = Product.objects.values_list('id', 'title')  # it returns a tuple

    query_set = OrderItem.objects.values('product_id').distinct()
    query_set = Product.objects.filter(id__in=OrderItem.objects.values('product_id').distinct())  # all the products have been ordered

    query_set = Product.objects.select_related('collection').all()  # join product with collection in 1 to many relatoin
    query_set = Product.objects.prefetch_related('promotions').all()

    query_set = Order.objects.select_related('customer').order_by('placed_at')[:5].values('id')
    query_set = Order.objects.select_related('customer').prefetch_related('orderitem_set').order_by('placed_at')[:5]
    query_set = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('placed_at')[:5]

    number_of_products = Product.objects.aggregate(Count('id'))  # number of all product it returns dictionary like this {'id__count': 1000}
    # we can change the name of the key in that dictionary like this Product.objects.aggregate(count=Count('id'))
    # now it returns {'count': 1000}
    number_of_products = Product.objects.aggregate(count=Count('id'), min_price=Min('unit_price'))
    number_of_products_with_collection_id_1 = Product.objects.filter(collection__id=1).aggregate(count=Count('id'), min_price=Min('unit_price'))
    number_of_products_with_collection_id_1 = Product.objects.filter(collection_id=1).aggregate(count=Count('id'), min_price=Min('unit_price'))
    number_of_orders = Order.objects.all().count()  # way 1
    number_of_orders = Order.objects.aggregate(Count('id'))
    number_of_product_1_have_been_sold = OrderItem.objects.filter(product_id=1).aggregate(Count('quantity'))
    orders_with_customer_1 = Order.objects.filter(customer_id=1).aggregate(Count('id'))
    res = Product.objects.filter(collection_id=3).aggregate(Min('unit_price'), Max('unit_price'), Avg('unit_price'))
    new_column = Customer.objects.annotate(is_new=Value(True))
    new_column_id = Customer.objects.annotate(new_id=F('id') + 1)

    # way 1
    first_functoin = Customer.objects.annotate(
        full_name=Func(
            F('first_name'), Value(' '), F('last_name'), function='CONCAT'
        )
    )
    # way 2
    first_functoin = Customer.objects.annotate(full_name=Concat('first_name', Value(' '), 'last_name'))

    number_of_orders_each_customer_commited = Customer.objects.annotate(orders_count=Count('order'))  # we use order instead of order_set and the reason is not clear
    number_of_orders_each_customer_commited2 = Order.objects.values('customer').annotate(Count('customer'))
    discounted_price = ExpressionWrapper(F('unit_price') * 0.8, output_field=DecimalField())
    query_set = Product.objects.annotate(discount_price=discounted_price)

    content_type = ContentType.objects.get_for_model(Product)
    query_set = TagItem.objects\
        .select_related('tag')\
        .filter(content_type=content_type, object_id=1)

    query_set = TagItem.objects.get_tags_for(content_type, 1)

    """update statement"""
    a = Collection.objects.filter(pk=11).update(featured_product=Product(pk=11))
    Collection.objects.filter(pk=11).update(featured_product=Product.objects.get(pk=12))
    Collection.objects.filter(pk=11).update(featured_product=16)

    with transaction.atomic():
        order = Order()
        order.customer_id = 1
        order.save()

        item = OrderItem()
        item.order = order
        item.product_id = 1
        item.quantity = 1
        item.unit_price = 11
        item.save()



    # with connection.cursor() as cursor:
    #     cursor.execute('SELECT * FROM store_customer')

    # cursor = connection.cursor()
    # cursor.execute('SELECT * FROM store_customer')
    # cursor.close()

    # query_set = Customer.objects.raw('SELECT * FROM store_customer')

    # with connection.cursor() as cursor:
    #     cursor.callproc('get_target_customer', [3])  #  calling store procedure
    product = Product.objects.get(pk=1)
    query_set = product.orderitem_set.all()
    # query_set = Product.objects.annotate(Count('collection'))
    # query_set = Customer.objects.annotate(Count('membership'))

    query_set = Order.objects.annotate(Count('orderitem'))

    # Customer.objects.filter(pk=2).update(membership='G')
    # Customer.objects.filter(pk=1).update(membership='S')
    # Product.objects.filter(pk=1).update(collection=Collection(pk=3))

    return render(request, 'how.html', context={'products': query_set})






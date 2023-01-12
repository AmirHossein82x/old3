from django_filters.rest_framework import FilterSet
from .models import Product
class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            'collection_id': ['exact'],
            'unit_price': ['lt', 'gt']   # we can swap lt with gt it does not matter in this case lt will appear above the gt
        }
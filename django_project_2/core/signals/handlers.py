from store.singnals import order_created
from django.dispatch import receiver

@receiver(order_created)
def on_order_created(sender, **kwargs):
    print(kwargs)
    print(kwargs['order'])
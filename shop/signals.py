from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from .models import *
from django.core.cache import cache
from .utils import *

@receiver([post_save,post_delete],sender=Product)
def invalidate_product_cache(sender,instance,**kwargs):
    print("Clearing product cache")
    cache.delete_pattern('*product_list*')

@receiver([post_save,post_delete],sender=Category)
def invalidate_category_cache(sender,instance,**kwargs):
    print("Clearing Category cache")
    clear_category_cache()

    # cache.delete_pattern('*category_list*')

@receiver([post_save,post_delete],sender=Table)
def invalidate_table_cache(sender,instance,**kwargs):
    print("Clearing table cache")
    clear_table_cache()
from django.core.cache import cache

def clear_category_cache():
    cache.delete_pattern('category_list*')
    cache.delete_pattern('views.decorators.cache.cache_page.category_list*')

def clear_table_cache():
    cache.delete_pattern('table_list*')
    cache.delete_pattern('views.decorators.cache.cache_page.table_list*')
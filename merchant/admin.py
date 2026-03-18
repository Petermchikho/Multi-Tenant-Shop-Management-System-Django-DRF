from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Merchant)
# admin.site.register(Shop)
admin.site.register(ShopType)

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'deleted_at')
    actions = ['restore_shops']
    list_filter = ('status',)
    readonly_fields = ('deleted_at',)

    def get_queryset(self, request):
        return Shop.all_objects.all()

    def delete_model(self, request, obj):
        obj.delete()  # soft delete

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()

    @admin.action(description='Restore selected shops')
    def restore_shops(self, request, queryset):
        for obj in queryset:
            obj.restore()



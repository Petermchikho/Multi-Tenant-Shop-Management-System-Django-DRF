from django.db import models
from decimal import Decimal
from shop.models import Shop,Product
from django.utils.timezone import now

class DailyOrderRevenue(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    date = models.DateField()  # the day this row represents
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        unique_together = ('shop', 'date')
        indexes = [
            models.Index(fields=['shop', 'date']),
        ]

    def __str__(self):
        return f"{self.shop} - {self.date} - {self.total_revenue}"

class DailyProductSales(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateField(default=now)
    total_quantity = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ('product', 'date')

    def __str__(self):
        return f"{self.product.name} - {self.date} ({self.total_quantity} sold)"

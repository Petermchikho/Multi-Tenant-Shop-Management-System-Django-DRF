from celery import shared_task
from django.utils.timezone import now
from .models import DailyOrderRevenue
from shop.models import Order
from django.core.mail import send_mail
from django.db.models import Sum, F
from .models import DailyProductSales
from shop.models import OrderItem

@shared_task
def update_daily_revenue_task():
    date = now().date()
    orders = Order.objects.filter(created_at__date=date)
    shops = orders.values('shop').distinct()

    for shop_entry in shops:
        shop_id = shop_entry['shop']
        shop_orders = orders.filter(shop_id=shop_id,status='paid')
        total_revenue = sum(order.total_amount for order in shop_orders)
        total_orders = shop_orders.count()

        DailyOrderRevenue.objects.update_or_create(
            shop_id=shop_id,
            date=date,
            defaults={
                'total_orders': total_orders,
                'total_revenue': total_revenue
            }
        )
        send_mail('Daily Revenue Task', f'Completed the daily revenue task for {date}', 'info@mobipay.mw', ['developers@mobipay.mw'])
    return f"Daily revenue updated for {date}"

@shared_task
def update_daily_product_sales():
    date = now().date()
    items = (
        OrderItem.objects
        .filter(order__created_at__date=date, order__status="paid")
        .values("product")
        .annotate(total_qty=Sum("quantity"),
                  total_rev=Sum(F("quantity") * F("product__price")))
    )

    for item in items:
        DailyProductSales.objects.update_or_create(
            product_id=item["product"],
            date=date,
            defaults={
                "total_quantity": item["total_qty"],
                "total_revenue": item["total_rev"],
            }
        )
    return f"Product sales summary updated for {date}"

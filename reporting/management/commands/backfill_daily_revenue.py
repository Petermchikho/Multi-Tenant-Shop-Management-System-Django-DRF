from django.core.management.base import BaseCommand
from django.db.models import Sum, Count
from django.utils.timezone import now
from ...models import DailyOrderRevenue
from shop.models import Order
from datetime import timedelta

class Command(BaseCommand):
    help = 'Backfill daily order revenue for existing orders'

    def handle(self, *args, **options):
        # Determine the date range
        first_order = Order.objects.order_by('created_at').first()
        if not first_order:
            self.stdout.write("No orders found.")
            return

        start_date = first_order.created_at.date()
        end_date = now().date()

        self.stdout.write(f"Backfilling daily revenue from {start_date} to {end_date}...")

        current_date = start_date
        while current_date <= end_date:
            orders = Order.objects.filter(created_at__date=current_date)
            shops = orders.values('shop').distinct()

            for shop_entry in shops:
                shop_id = shop_entry['shop']
                shop_orders = orders.filter(shop_id=shop_id,status='paid')
                total_revenue = sum(order.total_amount for order in shop_orders)
                total_orders = shop_orders.count()

                DailyOrderRevenue.objects.update_or_create(
                    shop_id=shop_id,
                    date=current_date,
                    defaults={
                        'total_orders': total_orders,
                        'total_revenue': total_revenue
                    }
                )

            self.stdout.write(f"Processed {current_date}")
            current_date += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS('Backfill completed successfully!'))

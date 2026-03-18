from django.core.management.base import BaseCommand
from django.db.models import Sum, F
from django.utils.timezone import make_aware
from datetime import timedelta, datetime
from shop.models import OrderItem
from reporting.models import DailyProductSales

class Command(BaseCommand):
    help = "Backfill daily product sales summaries for past orders"

    def add_arguments(self, parser):
        parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD)")
        parser.add_argument("--end", type=str, help="End date (YYYY-MM-DD)")

    def handle(self, *args, **options):
        start = datetime.fromisoformat(options["start"])
        end = datetime.fromisoformat(options["end"])

        current = start
        while current <= end:
            items = (
                OrderItem.objects
                .filter(order__created_at__date=current.date(), order__status="paid")
                .values("product")
                .annotate(total_qty=Sum("quantity"),
                          total_rev=Sum(F("quantity") * F("product__price")))
            )

            for item in items:
                DailyProductSales.objects.update_or_create(
                    product_id=item["product"],
                    date=current.date(),
                    defaults={
                        "total_quantity": item["total_qty"],
                        "total_revenue": item["total_rev"],
                    }
                )
            self.stdout.write(self.style.SUCCESS(f"Processed {current.date()}"))
            current += timedelta(days=1)
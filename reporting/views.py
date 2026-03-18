from rest_framework.views import APIView
from rest_framework.response import Response
from api.pagination import StandardResultsSetPagination
from django.db.models import Sum, Avg, Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from .models import DailyOrderRevenue

class PaginatedRevenueProgressionAPI(APIView):
    def get(self, request):
        shop_id = request.GET.get('shop')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        period = request.GET.get('period', 'day')  # 'day', 'week', 'month'

        revenue_qs = DailyOrderRevenue.objects.all()

        # Filters
        if shop_id:
            revenue_qs = revenue_qs.filter(shop__id=shop_id)
        if start_date and end_date:
            revenue_qs = revenue_qs.filter(date__range=[start_date, end_date])

        # Aggregation by period
        if period == 'day':
            queryset = (
                revenue_qs
                .annotate(period=TruncDay('date'))
                .values('period','shop','total_revenue','total_orders')
                .order_by('period')
            )
        elif period == 'week':
            queryset = (
                revenue_qs
                .annotate(period=TruncWeek('date'))
                .values('period','shop','total_revenue','total_orders')
                .order_by('period')
            )
        elif period == 'month':
            queryset = (
                revenue_qs
                .annotate(period=TruncMonth('date'))
                .values('period','shop','total_revenue','total_orders')
                .order_by('period')
            )
        else:
            queryset = []

        # Pagination
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(list(queryset), request)
        return paginator.get_paginated_response(page)

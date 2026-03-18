from rest_framework.pagination import PageNumberPagination
import math
from rest_framework.response import Response

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        total_items = self.page.paginator.count
        page_size = self.get_page_size(self.request)
        current_page = self.page.number
        total_pages = math.ceil(total_items / page_size)

        next_page_number = self.page.next_page_number() if self.page.has_next() else None
        previous_page_number = self.page.previous_page_number() if self.page.has_previous() else None

        # Compute a limited range of page numbers (up to 7)
        display_range = 7
        half_range = display_range // 2
        start_page = max(current_page - half_range, 1)
        end_page = min(start_page + display_range - 1, total_pages)

        # Adjust start_page if we are at the end
        start_page = max(end_page - display_range + 1, 1)
        page_range = list(range(start_page, end_page + 1))

        return Response({
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': current_page,
            'next_page_number': next_page_number,
            'previous_page_number': previous_page_number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_range': page_range,   # <-- added for frontend
            'results': data,
        })
    
class SmallResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        total_items = self.page.paginator.count
        page_size = self.get_page_size(self.request)
        current_page = self.page.number
        total_pages = math.ceil(total_items / page_size)

        next_page_number = self.page.next_page_number() if self.page.has_next() else None
        previous_page_number = self.page.previous_page_number() if self.page.has_previous() else None

        # Compute a limited range of page numbers (up to 7)
        display_range = 7
        half_range = display_range // 2
        start_page = max(current_page - half_range, 1)
        end_page = min(start_page + display_range - 1, total_pages)

        # Adjust start_page if we are at the end
        start_page = max(end_page - display_range + 1, 1)
        page_range = list(range(start_page, end_page + 1))

        return Response({
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': current_page,
            'next_page_number': next_page_number,
            'previous_page_number': previous_page_number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_range': page_range,   # <-- added for frontend
            'results': data,
        })

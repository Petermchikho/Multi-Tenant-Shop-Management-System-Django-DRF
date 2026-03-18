from django.urls import path
from . views import *
urlpatterns=[
    path('revenue',PaginatedRevenueProgressionAPI.as_view())
]
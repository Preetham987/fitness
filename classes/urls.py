from django.urls import path
from .views import (
    HomeView, ClassListView, BookClassView, BookingListView,
    ClassListHTML, BookClassHTML, BookingListHTML
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    # API endpoints
    path('classes', ClassListView.as_view(), name='api-classes'),
    path('book', BookClassView.as_view(), name='api-book'),
    path('bookings', BookingListView.as_view(), name='api-bookings'),

    # HTML views
    path('html/classes', ClassListHTML.as_view(), name='html-classes'),
    path('html/book', BookClassHTML.as_view(), name='html-book'),
    path('html/bookings', BookingListHTML.as_view(), name='html-bookings'),
]

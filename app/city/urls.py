from django.urls import path

from .views import (
    IndexView, HistoryListView, repeat_view,
)

urlpatterns = [
    # связываем представления с URL-адресами страниц
    path('', IndexView.as_view(), name='index'),
    path('history/', HistoryListView.as_view(), name='history'),
    path('repeat/<str:cname>/', repeat_view, name='repeat')
]

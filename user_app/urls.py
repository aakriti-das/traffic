from django.urls import path, re_path
from . import views
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),
    re_path(r'^[Rr]ecords/?$', views.records, name='records'),  # Handles both /records/ and /Records/
    path('video_feed/', views.video_feed, name='video_feed'),
    path('api/records/', views.get_records, name='get_records'),
    path('download-csv/', views.download_csv, name='download_csv'),
]
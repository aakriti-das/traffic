from django.urls import path, re_path
from . import views
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.welcome_dashboard, name='welcome_dashboard'),
    path('station-register/', views.station_register, name='station_register'),
    path('station-logout/', views.station_logout, name='station_logout'),
    re_path(r'^[Rr]ecords/?$', views.Records, name='Records'),  # Handles both /records/ and /Records/
    path('video_feed/', views.video_feed, name='video_feed'),
    path('api/records/', views.get_records, name='get_records'),
    path('download-csv/', views.download_csv, name='download_csv'),
]
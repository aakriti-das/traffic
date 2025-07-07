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
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/clear/', views.clear_notifications, name='clear_notifications'),
    path('notifications/stats/', views.get_notification_stats, name='get_notification_stats'),
    path('about/',views.about,name='about'),
    path('api/records/', views.get_records, name='get_records'),
    path('download-csv/', views.download_csv, name='download_csv'),
]
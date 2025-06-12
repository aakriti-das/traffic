from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),
    # path('records/', views.records, name='records'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('api/records/', views.get_records, name='get_records'),


]
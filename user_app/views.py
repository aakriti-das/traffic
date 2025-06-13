from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from .models import Record
from django.http import HttpResponseRedirect, HttpResponse,StreamingHttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from speed_estimation.main import process_video_stream
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .serialization import RecordSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.core.cache import cache
from django.conf import settings
from datetime import timedelta
import csv
from datetime import datetime

@ensure_csrf_cookie
def home(request):
    record_list = Record.objects.all()
    return render(request, 'base.html', {'record_list': record_list})


def Records(request):
    if not request.user.is_authenticated:
        return redirect('welcome_page')
    Record_list = Record.objects.all()
    context = {
        'Record_list': Record_list
    }
    return render(request, 'Records.html', context)

def video_feed(request):
    """
    Video streaming view that returns a video feed.
    """
    return StreamingHttpResponse(process_video_stream(), content_type='multipart/x-mixed-replace; boundary=frame')

class RecordPagination(PageNumberPagination):
    page_size = 7
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET'])
def get_records(request):
    if not request.user.is_authenticated:
        return redirect('welcome_page')
    records = Record.objects.all()
    serializer = RecordSerializer(records, many=True, context={'request': request})
    return Response(serializer.data)
def download_csv(request):
    """
    View for downloading records as CSV file.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="traffic_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'License Plate', 'Speed', 'Date', 'Status'])
    
    records = Record.objects.all().order_by('-date')
    for record in records:
        writer.writerow([
            record.id,
            record.licenseplate_no or 'N/A',
            record.speed,
            record.date.strftime('%Y-%m-%d'),
            'Exceeding' if record.speed > 50 else 'Normal'
        ])
    
    return response

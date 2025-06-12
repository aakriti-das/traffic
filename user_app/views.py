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

@ensure_csrf_cookie
def records(request):
    record_list = Record.objects.all()
    return render(request, 'records.html', {'record_list': record_list})

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
    try:
        # Check authentication
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Try to get cached records
        cache_key = f'records_page_{request.GET.get("page", 1)}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Get records and paginate
        records = Record.objects.all().order_by('-date')
        paginator = RecordPagination()
        paginated_records = paginator.paginate_queryset(records, request)
        
        # Serialize data
        serializer = RecordSerializer(paginated_records, many=True, context={'request': request})
        response_data = {
            'results': serializer.data,
            'count': records.count(),
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link()
        }

        # Cache the response for 5 seconds
        cache.set(cache_key, response_data, 5)

        return Response(response_data)

    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

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

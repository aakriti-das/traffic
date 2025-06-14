from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from .models import Record,Station
from .forms import StationSignUpForm ,StationLoginForm
from django.http import HttpResponse,StreamingHttpResponse
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
import uuid
from datetime import datetime
from speed_estimation.config import speed_limit

def station_register(request):
    mac_address=get_mac_address()
    if request.method == 'POST':
        form = StationSignUpForm(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            return redirect('welcome_dashboard')  # or a success page
    else:
        form = StationSignUpForm(initial={'mac_address':mac_address})
    return render(request, 'stationRegister.html', {'form': form})

def welcome_dashboard(request):
    error_message = None

    if request.method == 'POST':
        form = StationLoginForm(request.POST)
        if form.is_valid():
            areacode = form.cleaned_data['areacode']
            mac_address = get_mac_address()

            try:
                station = Station.objects.filter(areacode=areacode, mac_address=mac_address).first()
                if station:
                    request.session['station_id'] = station.id
                    return redirect('home')
                else:
                    error_message = "Invalid credentials. Please try again." 
            except Station.DoesNotExist:
                error_message = "Invalid credentials. Please try again."
    else:
        form = StationLoginForm()
    return render(request, 'welcome_dashboard.html', {'form': form, 'error_message': error_message})

def station_logout(request):
    request.session.flush()
    return redirect('welcome_dashboard')

@ensure_csrf_cookie
def home(request):
    station_id = request.session.get('station_id')
    if 'station_id' not in request.session:
        return redirect('welcome_dashboard')
    try:
        station = Station.objects.get(id=station_id)
    except Station.DoesNotExist:
        return redirect('welcome_dashboard')
    record_list = Record.objects.all()
    return render(request, 'base.html', {'record_list': record_list,'station':station})

def Records(request):
    if 'station_id' not in request.session:
        return redirect('welcome_dashboard')
    Record_list = Record.objects.all()
    context = {
        'Record_list': Record_list,
        'speed_limit':speed_limit
    }
    return render(request, 'Records.html', context)

def video_feed(request):
    return StreamingHttpResponse(process_video_stream(), content_type='multipart/x-mixed-replace; boundary=frame')

class RecordPagination(PageNumberPagination):
    page_size = 7
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET'])
def get_records(request):
    if 'station_id' not in request.session:
        return redirect('welcome_dashboard')
    records = Record.objects.all()
    serializer = RecordSerializer(records, many=True, context={'request': request})
    return Response(serializer.data)

def download_csv(request):
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
            'Exceeding' if record.speed > speed_limit else 'Normal'
        ])
    
    return response

def get_mac_address():
    mac = uuid.getnode()
    return ':'.join(['{:02x}'.format((mac >> ele) & 0xff)
                    for ele in range(0, 8 * 6, 8)][::-1])

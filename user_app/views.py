from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from .models import Record
from django.http import HttpResponseRedirect, HttpResponse,StreamingHttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from speed_estimation.main import process_video_stream



@ensure_csrf_cookie
def home(request):
    record_list = Record.objects.all()
    return render(request, 'base.html', {'record_list': record_list})

@ensure_csrf_cookie
def records(request):
    record_list = Record.objects.all()
    return render(request, 'Records.html', {'record_list': record_list})

def video_feed(request):
    """
    Video streaming view that returns a video feed.
    """
    return StreamingHttpResponse(process_video_stream(), content_type='multipart/x-mixed-replace; boundary=frame')
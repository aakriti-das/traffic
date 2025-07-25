from django.core.files import File
from django.utils import timezone
from django.contrib import messages
import cv2,uuid
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from user_app.models import Record, Station,Vehicle, Alert
from notification.mail import send_mail

def save_record(request,speed: int, count: int, vehicle_image_path: str, license_plate_image_path: str = None, licenseplate_no: str = None, station: Station = None):
    station_id = request.session.get('station_id')
    station = Station.objects.get(id=station_id) if station_id else Station.objects.first()
    
    record = Record(
        stationID=station,
        speed=speed,
        date=timezone.now().date(),
        count=count,
        licenseplate_no=licenseplate_no
    )

    # Save vehicle image
    if vehicle_image_path:
        with open(vehicle_image_path, "rb") as f:
            record.vehicle_image.save(
                f"vehicle_{timezone.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                File(f),
                save=False
            )

    # Save license plate image if provided
    if license_plate_image_path:
        with open(license_plate_image_path, "rb") as f:
            record.license_plate_image.save(
                f"licenseplate_{timezone.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                File(f),
                save=False
            )
    record.save()
    return record


def match_license_plate(request, record):
    record_license_plate = record.licenseplate_no 

    matching_vehicles = Vehicle.objects.filter(licenseplate_no=record_license_plate)
    print(f"Matching vehicles for license plate {record_license_plate}: {matching_vehicles.count()}")
    if matching_vehicles.exists():
        for vehicle in matching_vehicles:
            vehicle.violation_count = vehicle.violation_count + 1
            vehicle.save()
            print(f"Speeding Vehicle Owner:{vehicle.owner_name} \n Contact Number:{vehicle.contact_number} Email:{vehicle.email_id}")
            print(f"Overspeeded for {vehicle.violation_count}th time")
            
            # Enhanced alert message
            alert_message = f'🚨 SPEEDING ALERT: Vehicle {record.licenseplate_no} detected at {record.speed} km/h! Owner: {vehicle.owner_name} | Contact: {vehicle.contact_number} | Violations: {vehicle.violation_count}'
            
            # Save alert to database instead of session
            try:
                alert = Alert.objects.create(
                    station= record.stationID,
                    alert_type='warning',
                    message=alert_message,
                    vehicle_id=vehicle.id,
                    speed=record.speed,
                    violation_count=vehicle.violation_count
                )
                print(f"Alert saved to database: {alert_message}")
            except Exception as e:
                print(f"Error saving alert: {e}")
            
            # Also add to session for immediate access (optional)
            alerts = request.session.get('alerts', [])
            alerts.append({
                'type': 'warning',
                'message': alert_message,
                'timestamp': timezone.now().isoformat(),
                'vehicle_id': vehicle.id,
                'speed': record.speed,
                'violation_count': vehicle.violation_count
            })
            request.session['alerts'] = alerts
            request.session.modified = True
            
            # Send email notification
            FineAmount = 500
            body = f"Mr/Mrs. {vehicle.owner_name}, you have been fined Rs{FineAmount} for overspeeding the vehicle with LicensePlate {record.licenseplate_no}  at {record.speed} km/h at station {record.stationID.location}. This is violation #{vehicle.violation_count}."
            email = vehicle.email_id
            send_mail(body, [email])
            
            print(f"Alert saved to database: {alert_message}")

def get_mac_address():
    mac = uuid.getnode()
    return ':'.join(['{:02x}'.format((mac >> ele) & 0xff)
                    for ele in range(0, 8 * 6, 8)][::-1])

def get_speed_limit():
    try:
        mac_address=get_mac_address()
        station=Station.objects.get(mac_address=mac_address)
        return station.speed_limit
    except:
        return 20.0

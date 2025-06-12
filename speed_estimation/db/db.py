from django.core.files import File
from django.utils import timezone
import cv2
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from user_app.models import Record, Station,Vehicle
from speed_estimation.config import MAC_ADDRESS

def save_record(speed: int,count: int,vehicle_image_path: str,license_plate_image_path: str = None,licenseplate_no: str = None,station: Station = None):
    if station is None:
        station = Station.objects.first()
    if station is None:
        station=Station(
            areacode=23,
            location="Baneshwor",
            mac_address=MAC_ADDRESS
        )
        station.save()
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

def update_record(record_id: int,licenseplate_no: str = None,license_plate_image_np: any = None):
    try:
        record = Record.objects.get(id=record_id)
        print("Record:",record)
    except Record.DoesNotExist:
        raise ValueError(f"No record found with id {record_id}")
    if licenseplate_no:
        record.licenseplate_no = licenseplate_no

    if license_plate_image_np is not None:
        image_file = numpy_to_django_file(license_plate_image_np, f"licenseplate_{record.id}.jpg")
        record.license_plate_image.save(image_file.name, image_file, save=False)

    record.save()
    return record

def match_license_plate(record):
    record_license_plate=record.licenseplate_no 

    matching_vehicles=Vehicle.objects.filter(licenseplate_no=record_license_plate)

    if matching_vehicles.exists():
        for vehicle in matching_vehicles:
            print(f"Speeding Vehicle Owner:{vehicle.owner_name} \n Contact Number:{vehicle.contact_number}")
            # send_sms(vehicle.contact_number)

def numpy_to_django_file(np_image, filename="licenseplate.jpg"):
    # Convert OpenCV BGR to RGB
    img_rgb = cv2.cvtColor(np_image, cv2.COLOR_BGR2RGB)
    # Convert to PIL image
    pil_img = Image.fromarray(img_rgb)

    # Save to BytesIO buffer
    buffer = BytesIO()
    pil_img.save(buffer, format='JPEG')
    image_file = ContentFile(buffer.getvalue(), name=filename)

    return image_file

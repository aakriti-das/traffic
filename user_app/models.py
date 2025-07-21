from django.db import models

# Create your models here.

class Station(models.Model):
    areacode = models.PositiveIntegerField()
    location = models.CharField(max_length=80)
    mac_address = models.CharField(max_length=17)
    speed_limit = models.IntegerField(default=30)

    def __str__(self):
        return self.location

class Record(models.Model):
    stationID = models.ForeignKey('Station', on_delete=models.CASCADE)
    speed = models.IntegerField()
    date = models.DateField()
    count = models.IntegerField()
    # speed_limit=models.IntegerField()
    licenseplate_no = models.CharField(max_length=50, null=True)
    vehicle_image = models.ImageField(upload_to='Vehicle_images/', default=None, null=True, blank=True)
    license_plate_image = models.ImageField(upload_to='License_plate_images/', default='test_images/licenseplate_0_0.jpg', null=True, blank=True)

    def __str__(self):
        return f"Record from {self.stationID}"
    
class Vehicle(models.Model):
    owner_name=models.CharField(max_length=50,null=True)
    licenseplate_no =models.CharField(max_length=50,null=True)
    contact_number=models.CharField(max_length=20,null=True)
    violation_count=models.IntegerField(default=0)
    email_id=models.EmailField(null=True,blank=True)

    def __str__(self):
        return f"Vehicle{self.id}"

class Alert(models.Model):
    ALERT_TYPES = [
        ('warning', 'Warning'),
        ('danger', 'Danger'),
        ('info', 'Info'),
    ]
    
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPES, default='warning')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    vehicle_id = models.IntegerField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)
    violation_count = models.IntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.alert_type}: {self.message[:50]}"
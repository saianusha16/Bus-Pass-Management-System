from django.db import models
from django.conf import settings


class studentregistermodel(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=20)
    mobile = models.CharField(unique=True,max_length=20)
    status = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

from datetime import date

class ApplicantDetails(models.Model):
    name = models.CharField(max_length=20)
    father_guardian_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    age_as_on = models.DateField(default=date.today)  # Set default to today's date
    gender = models.CharField(max_length=6)
    aadhaar_no = models.CharField(max_length=12, unique=True)
    mobile = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    photo = models.ImageField(upload_to='photos/')

    def __str__(self):
        return self.name


class ResidentialAddress(models.Model):
    applicant = models.OneToOneField(ApplicantDetails, on_delete=models.CASCADE, related_name="residential_address")
    address = models.TextField(max_length=20)  # Limiting to 20 characters as shown in the screenshot
    district = models.CharField(max_length=50)  # Set default as needed
    village = models.CharField(max_length=50)
    pincode = models.CharField(max_length=6)  # Assuming pincode is 6 digits in India

    def __str__(self):
        return f"{self.address}, {self.district}, {self.pincode}"     


from django.db import models
from admins.models import Route  # Import Route model from the admin app
 # Import the ApplicantDetails model

import uuid  # For generating unique application numbers
from io import BytesIO
import qrcode
from django.core.files.base import ContentFile

from django.db import models
from admins.models import Route  # Import Route model from the admin app
from datetime import date

class RouteSelection(models.Model):
    MONTHLY = 'Monthly'
    QUARTERLY = 'Quarterly'
    ANNUAL = 'Annual'
    
    PASS_TYPES = [
        (MONTHLY, 'Monthly'),
        (QUARTERLY, 'Quarterly'),
        (ANNUAL, 'Annual'),
    ]
    
    applicant = models.ForeignKey(ApplicantDetails, on_delete=models.CASCADE, related_name='route_selections')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='route_selections')
    application_status = models.CharField(max_length=20, default='Pending')  # Pending, Approved, Rejected
    payment_status = models.CharField(max_length=20, default='Unpaid')  # Unpaid, Paid
    application_number = models.CharField(max_length=20, unique=True, blank=True)  # Auto-generated
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)  # Auto-generated QR Code
    pass_applied_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    pass_valid_upto = models.DateField()
    
    # New fields for Pass Type and Fare
    pass_type = models.CharField(max_length=10, choices=PASS_TYPES, default=MONTHLY)
    fare_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.application_number:
            # Generate unique application number
            self.application_number = f"APP-{uuid.uuid4().hex[:8].upper()}"
        
        if not self.qr_code:
            # Generate QR Code
            qr_data = f"Application Number: {self.application_number}\nName: {self.applicant.name}\nExpires: {self.pass_valid_upto}\nRoute: {self.route.start_point} to {self.route.end_point}"
            qr_image = qrcode.make(qr_data)
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            self.qr_code.save(f"{self.application_number}.png", ContentFile(buffer.getvalue()), save=False)
        
        # Calculate the fare based on the pass type
        if self.pass_type == self.MONTHLY:
            self.fare_amount = self.route.fare
        elif self.pass_type == self.QUARTERLY:
            self.fare_amount = self.route.fare * 3  # 3 months fare
        elif self.pass_type == self.ANNUAL:
            self.fare_amount = self.route.fare * 12  # 12 months fare
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Application {self.application_number} - {self.applicant.name}"


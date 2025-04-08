from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import ApplicantDetailsForm, ResidentialAddressForm, studentregistermodelform
from .models import studentregistermodel, ApplicantDetails, ResidentialAddress
from datetime import date
from django.http import HttpResponse
from django.template.loader import render_to_string
import pdfkit
from .models import RouteSelection
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from admins.models import Route
from datetime import timedelta
import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.urls import reverse
from admins.models import Route
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.conf import settings
import pdfkit
import re
from PIL import Image, ExifTags
import os
from django.core.mail import EmailMessage



# Create your views here.

def student(request):
    return render(request,'student.html')

def registercheck(request):
    if request.method == 'POST':
        form = studentregistermodelform(request.POST)
        if request.POST['password'] != request.POST['confirm_password']:
            messages.warning(request, 'Passwords do not match.')
        else:
            if form.is_valid():
                email = form.cleaned_data.get('email')
                mobile = form.cleaned_data.get('mobile')
                if studentregistermodel.objects.filter(email=email).exists():
                    messages.warning(request, 'Email is already registered.')
                elif studentregistermodel.objects.filter(mobile=mobile).exists():
                    messages.warning(request, 'Mobile number is already registered.')
                else:
                    form.save()
                    form = studentregistermodelform()
                    messages.success(request, 'Account created successfully! wait For ACTIVATION By Admin.')
                    return render(request, 'studentregistration.html', {'form': form})
            else:
                messages.warning(request, 'Please enter correct credentials.')
    else:
        form = studentregistermodelform()
    return render(request, 'studentregistration.html', {'form': form})


def UserLoginCheck(request):
    if request.method == "POST":
        email = request.POST.get('email')
        pswd = request.POST.get('pswd')
        print("Login email= ", email, ' Password = ', pswd)
        try:
            # Verify user credentials
            check = studentregistermodel.objects.get(email=email, password=pswd)
            status = check.status
            print('Status is = ', status)

            if status == "activated":
                # Set user session data
                request.session['id'] = check.id
                request.session['user_name'] = check.name
                request.session['email'] = check.email
                print("User id At", check.id, status)

                # Check if the user has already applied for a bus pass
                route_selection = RouteSelection.objects.filter(applicant__email=email).last()

                if route_selection:
                    # If the user has already applied, redirect to a dedicated page
                    application_number = route_selection.application_number
                    renewal_date = route_selection.pass_valid_upto
                    return render(request, 'students/AlreadyApplied.html', {
                        'application_number': application_number,
                        'renewal_date': renewal_date.strftime("%Y-%m-%d"),
                        'user_name': check.name
                    })

                # Logic for new applications
                return render(request, 'UserHomePage.html', {
                    'user_name': check.name,
                    'user_email': check.email,
                    'application_number': application_number if route_selection else None,
                    'renewal_date': renewal_date if route_selection else None

                })

            else:
                messages.error(request, 'Account is not activated.')
        except studentregistermodel.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
        except Exception as e:
            print('Exception is ', str(e))
            messages.error(request, 'An error occurred. Please try again.')
        return render(request, 'student.html', {'login_modal_open': True})

    return render(request, 'student.html', {})

def logoutfun(request):
    return render(request,'student.html')

from django.shortcuts import render, redirect
from .models import RouteSelection

def userhome(request):
    if 'user_name' not in request.session:
        return redirect('student')

    # Check if user has already applied for a bus pass
    user_email = request.session['email']
    route_selection = RouteSelection.objects.filter(applicant__email=user_email).last()

    if route_selection:
        return render(request, 'students/AlreadyApplied.html', {
            'user_name': request.session['user_name'],
            'user_email': request.session['email'],
            'application_number': route_selection.application_number,
            'renewal_date': route_selection.pass_valid_upto.strftime("%Y-%m-%d"),
        })

    # If no bus pass application, show the user home page
    return render(request, 'UserHomePage.html', {
        'user_name': request.session['user_name'],
        'user_email': request.session['email'],
    })


def alreadyapplied(request):
    if 'user_name' not in request.session:
        return redirect('student')

    return render(request, 'students/AlreadyApplied.html', {
        'user_name': request.session['user_name'],
        'user_email': request.session['email']
    })    

# -----------------------------------------------------------------------------------------------

def create_applicant(request):
    if 'email' not in request.session:
        messages.error(request, "You need to be logged in to create an applicant.")
        return redirect('student')  # Redirect to login if not logged in

    try:
        user = studentregistermodel.objects.get(email=request.session['email'])
    except studentregistermodel.DoesNotExist:
        messages.error(request, "No registered user found with the provided details.")
        return redirect('student')  # Redirect to login if user not found

    initial_applicant_data = {
        'name': user.name,
        'email': user.email,
        'mobile': user.mobile
    }
    applicant_form = ApplicantDetailsForm(initial=initial_applicant_data)
    address_form = ResidentialAddressForm()

    if request.method == 'POST':
        applicant_form = ApplicantDetailsForm(request.POST, request.FILES)
        address_form = ResidentialAddressForm(request.POST)

        if applicant_form.is_valid() and address_form.is_valid():
            applicant = applicant_form.save(commit=False)
            applicant.age_as_on = date.today()
            applicant.save()

            residential_address = address_form.save(commit=False)
            residential_address.applicant = applicant
            residential_address.save()

            messages.success(request, "Applicant and address details successfully created!")
            # Redirect to route selection page
            return redirect('route_selection', applicant_id=applicant.id)

        else:
            print("Applicant Form Errors:", applicant_form.errors)
            print("Address Form Errors:", address_form.errors)
            messages.error(request, "Please correct the errors below.")

    return render(request, 'applicant_form.html', {
        'applicant_form': applicant_form,
        'address_form': address_form,
        'user_name': user.name,
        'user_email': user.email,
        'user_mobile': user.mobile
    })

def route_selection(request, applicant_id):
    # Get the applicant object based on the applicant_id
    applicant = get_object_or_404(ApplicantDetails, id=applicant_id)
    routes = Route.objects.all()

    # Fetch the logged-in user using the session email
    if 'email' not in request.session:
        messages.error(request, "You need to be logged in to select a route.")
        return redirect('student')  # Redirect to login if not logged in

    try:
        user = studentregistermodel.objects.get(email=request.session['email'])
    except studentregistermodel.DoesNotExist:
        messages.error(request, "No registered user found with the provided details.")
        return redirect('student')  # Redirect to login if user not found

    # Handle POST request when the route is selected
    if request.method == 'POST':
        route_id = request.POST.get('route')
        pass_type = request.POST.get('pass_type')  # Get pass type from the form
        if not route_id or not pass_type:
            messages.error(request, "Please select a route and pass type.")
            return render(request, 'students/route_selection.html', {
                'applicant': applicant,
                'routes': routes,
                'user_name': user.name,  # Pass user details to the template if needed
                'user_email': user.email,
            })

        route = get_object_or_404(Route, id=route_id)

        # Generate unique application number
        application_number = f"APP-{uuid.uuid4().hex[:8].upper()}"

        # Calculate fare and pass validity based on the pass type
        if pass_type == 'Monthly':
            fare_amount = route.fare
            pass_valid_upto = timezone.now() + timedelta(days=30)  # 1 month validity
        elif pass_type == 'Quarterly':
            fare_amount = route.fare * 3  # 3 months fare
            pass_valid_upto = timezone.now() + timedelta(days=90)  # 3 months validity
        elif pass_type == 'Annual':
            fare_amount = route.fare * 12  # 12 months fare
            pass_valid_upto = timezone.now() + timedelta(days=365)  # 1 year validity

        # Create the RouteSelection instance
        route_selection = RouteSelection.objects.create(
            applicant=applicant,
            route=route,
            pass_type=pass_type,
            application_number=application_number,
            fare_amount=fare_amount,
            pass_valid_upto=pass_valid_upto,
            pass_applied_date=timezone.now(),
        )

        # Generate QR code for the application
        qr_data = f"Application Number: {application_number}\nName: {applicant.name}\nExpires: {pass_valid_upto}\nRoute: {route.start_point} to {route.end_point}"
        qr_image = qrcode.make(qr_data)
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        route_selection.qr_code.save(f"{application_number}.png", ContentFile(buffer.getvalue()), save=False)

        # Save RouteSelection instance to the database
        route_selection.save()

        # Redirect to display the fare amount page
        messages.success(request, "Your bus pass application has been successfully submitted.")
        return redirect('display_amount', route_selection_id=route_selection.id)

    # Render the route selection form
    return render(request, 'students/route_selection.html', {
        'applicant': applicant,
        'routes': routes,
        'user_name': user.name,  # Pass user details if needed in the template
        'user_email': user.email,
    })

# ----------------------------------------------------------------------------------------

def display_amount(request, route_selection_id):
    # Get the selected RouteSelection object
    route_selection = get_object_or_404(RouteSelection, id=route_selection_id)

    # Get the fare amount (calculated in the RouteSelection save method)    
    fare = route_selection.fare_amount

    # Pass route details, including the fare, to the template
    return render(request, 'admins/display_amount.html', {
        'route_selection': route_selection,
        'fare': fare,  # Display the fare calculated
        'application_status': route_selection.application_status,
        'payment_status': route_selection.payment_status,
        'application_number': route_selection.application_number,
        'qr_code': route_selection.qr_code,
        'pass_applied_date': route_selection.pass_applied_date,
        'pass_valid_upto': route_selection.pass_valid_upto, })


def payment_gateway(request, route_selection_id):
    # Fetch the RouteSelection instance
    route_selection = get_object_or_404(RouteSelection, id=route_selection_id)

    if request.method == 'POST':
        payment_option = request.POST.get('payment_option')

        # Validate payment details
        if payment_option == 'debit_card':
            card_number = request.POST.get('card_number')
            expiry_date = request.POST.get('expiry_date')
            cvv = request.POST.get('cvv')

            if not all([card_number, expiry_date, cvv]):
                return render(request, 'students/payment_gateway.html', {
                    'route_selection': route_selection,
                    'error': 'Please fill out all debit card details.',
                })

        elif payment_option == 'upi':
            upi_id = request.POST.get('upi_id')

            if not upi_id:
                return render(request, 'students/payment_gateway.html', {
                    'route_selection': route_selection,
                    'error': 'Please provide a valid UPI ID.',
                })

        elif payment_option == 'credit_card':
            card_number = request.POST.get('card_number')
            expiry_date = request.POST.get('expiry_date')
            cvv = request.POST.get('cvv')

            if not all([card_number, expiry_date, cvv]):
                return render(request, 'students/payment_gateway.html', {
                    'route_selection': route_selection,
                    'error': 'Please fill out all credit card details.',
                })

        else:
            return render(request, 'students/payment_gateway.html', {
                'route_selection': route_selection,
                'error': 'Invalid payment option selected.',
            })

        # Mock payment success
        route_selection.payment_status = 'Paid'
        route_selection.save()

        # Redirect to the payment_success page with the route_selection_id
        return redirect('payment_success', route_selection_id=route_selection.id)

    return render(request, 'students/payment_gateway.html', {'route_selection': route_selection})

def payment_success(request, route_selection_id):
    route_selection = get_object_or_404(RouteSelection, id=route_selection_id)
    applicant_name = route_selection.applicant.name
    
    # Generate PDF for the bus pass
    photo_url = request.build_absolute_uri(route_selection.applicant.photo.url)
    qr_code_url = request.build_absolute_uri(route_selection.qr_code.url)

    html_content = render_to_string('students/final_pass.html', {
        'route_selection': route_selection,
        'photo_url': photo_url,
        'qr_code_url': qr_code_url,
        'is_pdf': True,
    })

    pdfkit_config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    options = {'enable-local-file-access': True}
    
    try:
        pdf_file = pdfkit.from_string(html_content, False, configuration=pdfkit_config, options=options)
    except Exception as e:
        print(f"PDF Generation Error: {e}")
        messages.error(request, "Failed to generate PDF for your bus pass.")
        return redirect('student')
    
    # Prepare email
    subject = 'Your Bus Pass Details'
    message = f"Dear {applicant_name},\n\nPlease find attached your bus pass and QR code.\n\nThank you for choosing our service."
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [route_selection.applicant.email]
    
    email = EmailMessage(subject, message, from_email, recipient_list)
    
    # Attach PDF
    email.attach(f"bus_pass_{route_selection.application_number}.pdf", pdf_file, 'application/pdf')
    
    # Attach QR Code
    qr_code_image = route_selection.qr_code.open('rb').read()
    email.attach(f"{route_selection.application_number}_qr.png", qr_code_image, 'image/png')
    
    try:
        email.send()
        messages.success(request, "Payment successful! Bus pass and QR code have been emailed to you.")
    except Exception as e:
        print(f"Email Error: {e}")
        messages.error(request, "Payment successful, but failed to send email with bus pass details.")
    
    return render(request, 'students/payment_redirect_message.html', {
        'route_selection': route_selection,
        'redirect_url': reverse('final_pass_html', kwargs={'route_selection_id': route_selection.id}),
        'applicant_name': applicant_name,
    })
# ---------------------------------------------------------------------------------------------------------
from django.shortcuts import get_object_or_404, render

def final_pass_html(request, route_selection_id):
    route_selection = get_object_or_404(RouteSelection, id=route_selection_id)
    
    # Absolute URLs for images
    photo_url = request.build_absolute_uri(route_selection.applicant.photo.url)
    qr_code_url = request.build_absolute_uri(route_selection.qr_code.url)
    
    # Pass absolute URLs to the template
    return render(request, 'students/final_pass.html', {
        'route_selection': route_selection,
        'photo_url': photo_url,
        'qr_code_url': qr_code_url,
    })


def search_bus_pass(request):
    applicant_name = None  # Default value for applicant name
    route_selection = None  # Default value for route selection

    if request.method == 'POST':
        search_field = request.POST.get('search_field')

        # Ensure search_field is a string and not None
        if not search_field:
            messages.error(request, "Please provide a search input (either application number, mobile number, or email).")
            return render(request, 'students/search_bus_pass.html')

        # Check if the search field contains a valid application number (e.g., APP-XXXXXX)
        if re.match(r'^APP-[A-F0-9]{8}$', search_field):  # Application number validation
            try:
                route_selection = RouteSelection.objects.get(application_number=search_field)
                # Ensure that the logged-in user is the applicant for this route_selection
                if route_selection.applicant.email == request.session.get('email'):
                    applicant_name = route_selection.applicant.name  # Get applicant name
                    return redirect('final_pass_html', route_selection_id=route_selection.id)
                else:
                    messages.error(request, "You can only search for your own bus pass.")
            except RouteSelection.DoesNotExist:
                messages.error(request, "No bus pass found with the provided application number.")
        
        # Check if the search field contains a valid mobile number (assuming 10 digits)
        elif re.match(r'^\d{10}$', search_field):  # Mobile number validation
            try:
                route_selection = RouteSelection.objects.get(applicant__mobile=search_field)
                # Ensure that the logged-in user is the applicant for this route_selection
                if route_selection.applicant.email == request.session.get('email'):
                    applicant_name = route_selection.applicant.name  # Get applicant name
                    return redirect('final_pass_html', route_selection_id=route_selection.id)
                else:
                    messages.error(request, "You can only search for your own bus pass.")
            except RouteSelection.DoesNotExist:
                messages.error(request, "No bus pass found with the provided mobile number.")
        
        # Check if the search field contains a valid email
        elif re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', search_field):  # Email validation
            try:
                route_selection = RouteSelection.objects.get(applicant__email=search_field)
                # Ensure that the logged-in user is the applicant for this route_selection
                if route_selection.applicant.email == request.session.get('email'):
                    applicant_name = route_selection.applicant.name  # Get applicant name
                    return redirect('final_pass_html', route_selection_id=route_selection.id)
                else:
                    messages.error(request, "You can only search for your own bus pass.")
            except RouteSelection.DoesNotExist:
                messages.error(request, "No bus pass found with the provided email address.")
        
        else:
            messages.error(request, "Please enter a valid application number, mobile number, or email address.")

    return render(request, 'students/search_bus_pass.html', {'applicant_name': applicant_name})

def correct_image_orientation(image_path):
    """
    Corrects the orientation of an image based on its EXIF data.
    """
    try:
        image = Image.open(image_path)
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = image._getexif()
        if exif is not None:
            orientation_value = exif.get(orientation, None)
            if orientation_value == 3:
                image = image.rotate(180, expand=True)
            elif orientation_value == 6:
                image = image.rotate(270, expand=True)
            elif orientation_value == 8:
                image = image.rotate(90, expand=True)
        # Save the corrected image back to the same path
        image.save(image_path)
    except Exception as e:
        print(f"Error correcting image orientation: {e}")


from django.shortcuts import render

def generate_pdf(request, route_selection_id):
    """
    Generates a PDF for the Smart Bus Pass.
    """
    route_selection = get_object_or_404(RouteSelection, id=route_selection_id)

    # Get the absolute path of the profile photo
    photo_path = route_selection.applicant.photo.path  # Get the local file path
    qr_code_path = route_selection.qr_code.path  # Local file path for QR code

    # Correct the orientation of the profile image
    correct_image_orientation(photo_path)

    # Generate absolute URLs for the corrected images
    photo_url = request.build_absolute_uri(route_selection.applicant.photo.url)
    qr_code_url = request.build_absolute_uri(route_selection.qr_code.url)

    print("Photo URL:", photo_url)
    print("QR Code URL:", qr_code_url)

    # Render HTML content with a context variable indicating PDF generation
    html_content = render_to_string('students/final_pass.html', {
        'route_selection': route_selection,
        'photo_url': photo_url,
        'qr_code_url': qr_code_url,
        'is_pdf': True,  # Add this context variable
    })

    # Configure pdfkit
    pdfkit_config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

    options = {
        'enable-local-file-access': True,  # Enable local file access for images
    }

    try:
        # Generate the PDF
        pdf_output = pdfkit.from_string(html_content, False, configuration=pdfkit_config, options=options)

        # Create the response for downloading
        response = HttpResponse(pdf_output, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="bus_pass_{route_selection.application_number}.pdf"'
        return response
    except OSError as e:
        return HttpResponse(f"PDF generation failed: {e}", status=500)





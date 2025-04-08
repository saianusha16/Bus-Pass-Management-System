from django import forms
from django.core.exceptions import ValidationError
from .models import studentregistermodel
import re

class studentregistermodelform(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter Your Name','autocomplete':'off'}), max_length=20, required=True)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control','placeholder':'Enter Valid Email To Get The Otp Ex:abcdef@gmail.com '}), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Create Your Password'}), max_length=20, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Confirm your Password'}), max_length=20, required=True)
    mobile = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter Your Mobile Number'}), max_length=20, required=True)
    status = forms.CharField(widget=forms.HiddenInput(), initial='waiting', max_length=100)

    class Meta:
        model = studentregistermodel
        fields = ['name', 'email', 'password', 'confirm_password', 'mobile','status']
    def clean_password(self):
        password = self.cleaned_data.get('password')
        errors = []

        if password:
            if len(password) < 8:
                errors.append("Password must be at least 8 characters long.")
            if not re.search(r"[A-Z]", password):
                errors.append("Password must contain at least one uppercase letter A-Z.")
            if not re.search(r"[a-z]", password):
                errors.append("Password must contain at least one lowercase letter a-z.")
            if not re.search(r"[0-9]", password):
                errors.append("Password must contain at least one digit 0-9.")
            if not re.search(r"[!@#$%^&*()_+]", password):
                errors.append("Password must contain at least one special character @,!,#.....")

        if errors:
            raise ValidationError(errors)

        return password
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        mobile = cleaned_data.get("mobile")
        if mobile and not re.match(r'^\d{10}$', mobile):
            self.add_error('mobile', "Invalid Mobile number.")

        return cleaned_data


# -------------------------------------------------------------
from .models import ApplicantDetails
class ApplicantDetailsForm(forms.ModelForm):
    class Meta:
        model = ApplicantDetails
        fields = ['name', 'father_guardian_name', 'date_of_birth', 'gender', 'aadhaar_no', 'mobile', 'email', 'photo']

    def __init__(self, *args, **kwargs):
        read_only = kwargs.pop('read_only', False)
        super(ApplicantDetailsForm, self).__init__(*args, **kwargs)

        if read_only:
            for field in ['name', 'email', 'mobile']:
                self.fields[field].widget.attrs['readonly'] = True

# ----------------------------------------------------------------------
from .models import ResidentialAddress

class ResidentialAddressForm(forms.ModelForm):
    class Meta:
        model = ResidentialAddress
        fields = ['address', 'district',  'village', 'pincode']

    def __init__(self, *args, **kwargs):
        super(ResidentialAddressForm, self).__init__(*args, **kwargs)
        self.fields['address'].widget.attrs.update({'maxlength': '20'})

#-----------------------------------------------------------------------

  
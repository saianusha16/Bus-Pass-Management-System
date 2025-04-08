from django import forms
from .models import Route

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['start_point', 'end_point', 'distance', 'fare']

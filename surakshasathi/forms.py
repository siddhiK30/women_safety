# forms.py
from django import forms
from .models import Marker

class MarkerAdminForm(forms.ModelForm):
    class Meta:
        model = Marker
        fields = ['lat', 'lng', 'safety_status']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lat'].widget = forms.NumberInput(attrs={'step': '0.000001'})
        self.fields['lng'].widget = forms.NumberInput(attrs={'step': '0.000001'})
        
    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get('lat')
        lng = cleaned_data.get('lng')
        
        if lat and (lat < -90 or lat > 90):
            raise forms.ValidationError('Latitude must be between -90 and 90 degrees')
            
        if lng and (lng < -180 or lng > 180):
            raise forms.ValidationError('Longitude must be between -180 and 180 degrees')
            
        return cleaned_data
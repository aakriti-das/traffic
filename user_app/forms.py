from django import forms
from .models import Station
import uuid

def get_mac_address():
    mac = uuid.getnode()
    return ':'.join(['{:02x}'.format((mac >> ele) & 0xff)
                    for ele in range(0, 8 * 6, 8)][::-1])

class StationSignUpForm(forms.ModelForm):
    class Meta:
        mac_address=get_mac_address()
        model = Station
        fields = ['areacode', 'location','mac_address', 'speed_limit']
        widgets = {
            'mac_address': forms.TextInput(attrs={'readonly': 'readonly'})
        }

class StationLoginForm(forms.Form):
    areacode = forms.IntegerField(label="Area Code")
    # mac_address = forms.CharField(label="MAC Address", max_length=17)
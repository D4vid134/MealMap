from xml.dom import ValidationErr
from django import forms

class NearbyRestaurantSearchForm(forms.Form):
    type = forms.CharField(max_length=100, required=False, initial=' ')
    min_rating = forms.DecimalField(min_value=0, max_value=5, initial=0)
    max_distance = forms.IntegerField()

class SpecificRestaurantSearchForm(forms.Form):
    name = forms.CharField(max_length=200, required=False)
    address = forms.CharField(max_length=250, required=False)
    keywords = forms.CharField(max_length=200, required=False, initial=' ')
    
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        address = cleaned_data.get('address')

        if not name and not address:
            raise ValidationErr("At least one of the fields (Name or Address) must be filled out.")

        return cleaned_data
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UsernameField

from .models import Beermat, Profile


class BeermatSubmissionForm(forms.ModelForm):
    class Meta:
        model = Beermat
        fields = [
            'photo_front',
            'photo_back',
            'name',
            'beer_name',
            'brewery',
            'country',
            'diameter_mm',
            'weight_g',
            'thickness_mm',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_fields = ['photo_front', 'photo_back', 'name', 'beer_name', 'brewery', 'country']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

    def clean(self):
        cleaned = super().clean()

        # Ensure required fields are provided (model fields are optional)
        required = ['photo_front', 'photo_back', 'name', 'beer_name', 'brewery', 'country']
        for field in required:
            if not cleaned.get(field):
                self.add_error(field, 'This field is required.')

        front = cleaned.get('photo_front')
        back = cleaned.get('photo_back')
        for field, file in [('photo_front', front), ('photo_back', back)]:
            if file and file.content_type not in ('image/jpeg', 'image/png'):
                self.add_error(field, 'Only JPEG and PNG files are allowed.')
        return cleaned


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'maxlength': 150}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email']
        field_classes = {'username': UsernameField}

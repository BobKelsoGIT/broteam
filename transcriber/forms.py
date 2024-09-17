from django import forms
from .models import MediaFile
from crispy_forms.helper import FormHelper


class MediaFileForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ['file']
        labels = {
            'file': ""
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'

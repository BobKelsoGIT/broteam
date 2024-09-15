from django import forms
from .models import VideoFile
from crispy_forms.helper import FormHelper


class VideoFileForm(forms.ModelForm):
    class Meta:
        model = VideoFile
        fields = ['video']
        labels = {
            'video': ""
        }
        label_suffix = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'

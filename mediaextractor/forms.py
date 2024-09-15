from django import forms
from .models import VideoFile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class VideoFileForm(forms.ModelForm):
    class Meta:
        model = VideoFile
        fields = ['video']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(
            Submit('submit', 'Upload', css_class='btn btn-primary w-100'))

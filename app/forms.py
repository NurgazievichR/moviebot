from django import forms
from .models import Project

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class UploadFilesForm(forms.Form):  
    project = forms.ModelChoiceField(queryset=Project.objects.all(), label="Выберите проект")
    files = MultipleFileField(label="Выберите файлы")

class UploadASMRForm(forms.Form):
    file = forms.FileField(label="Выберите ASMR видео")
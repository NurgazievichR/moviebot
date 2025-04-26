from django import forms
from .models import Project
from dev.models import FormatSettings
from django.core.exceptions import ValidationError

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

    def clean_files(self):
        files = self.cleaned_data.get('files')
        settings = FormatSettings.objects.first()

        if settings:
            allowed_exts = settings.get_allowed_list()
            for file in files:
                ext = file.name.split('.')[-1].lower()
                if ext not in allowed_exts:
                    raise ValidationError(f"Файл {file.name} имеет запрещённое расширение .{ext}.")

        return files

class UploadASMRForm(forms.Form):
    file = forms.FileField(label="Выберите ASMR видео")

    def clean_file(self):
        file = self.cleaned_data.get('file')
        settings = FormatSettings.objects.first()

        if settings:
            allowed_exts = settings.get_allowed_list()
            ext = file.name.split('.')[-1].lower()
            if ext not in allowed_exts:
                raise ValidationError(f"Файл {file.name} имеет запрещённое расширение .{ext}.")

        return file
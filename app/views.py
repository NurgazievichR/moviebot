import tempfile
import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required

from .forms import UploadFilesForm, UploadASMRForm
from .models import ProjectFile
from .tasks import cut_asmr_task

@login_required
def upload_files(request):
    if request.method == 'POST':
        form = UploadFilesForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.cleaned_data['project']
            files = request.FILES.getlist('files')
            for f in files:
                ProjectFile.objects.create(project=project, file=f)
            return redirect('upload_files')
    else:
        form = UploadFilesForm()

    uploaded_files = ProjectFile.objects.all().order_by('-uploaded_at') 
    return render(request, 'upload_files.html', {'form': form, 'uploaded_files': uploaded_files})

@login_required
def upload_asmr(request):
    if request.method == 'POST':
        form = UploadASMRForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']

            with tempfile.NamedTemporaryFile(delete=False, dir=settings.MEDIA_ROOT, suffix='.mp4') as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_input_path = temp_file.name

            temp_input_relpath = os.path.relpath(temp_input_path, settings.MEDIA_ROOT)

            cut_asmr_task.delay(temp_input_relpath)

            return redirect('upload_asmr')
    else:
        form = UploadASMRForm()

    return render(request, 'upload_asmr.html', {'form': form})
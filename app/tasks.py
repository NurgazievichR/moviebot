import os
import subprocess
from django.conf import settings
from celery import shared_task

from .models import ASMR, ProjectFile
from .scripts import randomize_video

@shared_task
def process_video(file_id):
    """Таска для обработки ProjectFile"""
    video = ProjectFile.objects.get(id=file_id)
    video.status = 'processing'
    video.save()

    input_path = os.path.join(settings.MEDIA_ROOT, video.file.name)
    output_dir = os.path.join(settings.MEDIA_ROOT, 'processed/')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'processed_{video.id}.mp4')

    randomize_video(input_path, output_path)

    video.status = 'ready'
    video.save()

    return f"Видео {video.file.name} обработано"

@shared_task
def cut_asmr_task(temp_input_relpath):
    """Таска для нарезки и обработки ASMR"""
    temp_input_path = os.path.join(settings.MEDIA_ROOT, temp_input_relpath)
    output_dir = os.path.join(settings.MEDIA_ROOT, 'asmr/chunks/')
    os.makedirs(output_dir, exist_ok=True)

    # Проверяем разрешение файла
    probe_command = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height', '-of', 'csv=s=x:p=0', temp_input_path
    ]
    resolution = subprocess.check_output(probe_command).decode().strip()
    width, height = map(int, resolution.split('x'))

    # Выбираем нужный масштаб
    if height > 720:
        scale_filter = "scale=1280:720"
    else:
        scale_filter = "scale=iw:ih"

    # Нарезаем видео
    segment_command = [
        'ffmpeg', '-i', temp_input_path,
        '-vf', scale_filter,
        '-an',  # убираем звук
        '-f', 'segment',
        '-segment_time', '10',
        '-c:v', 'libx264',
        '-preset', 'fast',
        f'{output_dir}/asmr_%03d.mp4'
    ]

    subprocess.run(segment_command, check=True)
    os.remove(temp_input_path)  # удаляем оригинал после нарезки

    # Обрабатываем каждый нарезанный кусок отдельно
    for filename in sorted(os.listdir(output_dir)):
        if filename.startswith('asmr_') and filename.endswith('.mp4'):
            original_chunk_path = os.path.join(output_dir, filename)

            # Создаём путь для обработанного файла
            processed_chunk_path = os.path.join(output_dir, f'processed_{filename}')

            randomize_video(original_chunk_path, processed_chunk_path)

            # Сохраняем только обработанный кусок в БД
            relative_processed_path = os.path.relpath(processed_chunk_path, settings.MEDIA_ROOT)
            ASMR.objects.create(file=relative_processed_path)

            # Удаляем необработанный оригинал куска
            os.remove(original_chunk_path)
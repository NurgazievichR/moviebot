import os
import subprocess
import shutil
from django.conf import settings
from celery import shared_task

from .models import ASMR, ProjectFile
from .scripts import randomize_video

@shared_task(queue='default')
def process_video(file_id):
    """Таска для обработки ProjectFile."""

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

    return f"Видео {video.file.name} обработано."

@shared_task(queue='asmr_cutting')
def cut_asmr_task(temp_input_relpath):
    """Таска для нарезки ASMR видео строго по 10 секунд. Удаляем слишком короткие видео."""

    temp_input_path = os.path.join(settings.MEDIA_ROOT, temp_input_relpath)
    chunks_dir = os.path.join(settings.MEDIA_ROOT, 'asmr/chunks/')
    ready_dir = os.path.join(settings.MEDIA_ROOT, 'asmr/ready/')

    os.makedirs(chunks_dir, exist_ok=True)
    os.makedirs(ready_dir, exist_ok=True)

    # 1. Узнаем длину видео
    duration_command = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        temp_input_path
    ]
    duration = float(subprocess.check_output(duration_command).decode().strip())

    # 2. Если меньше 10 секунд — удаляем файл и выходим
    if duration < 10:
        os.remove(temp_input_path)
        return

    # 3. Обрезаем исходное видео до длины, кратной 10
    usable_duration = (int(duration) // 10) * 10
    trimmed_path = os.path.join(chunks_dir, 'trimmed_input.mp4')

    trim_command = [
        'ffmpeg', '-y', '-i', temp_input_path,
        '-t', str(usable_duration),
        '-vf', 'scale=1280:720',  # фиксируем качество
        '-an',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-g', '25',
        '-keyint_min', '25',
        trimmed_path
    ]
    subprocess.run(trim_command, check=True)

    os.remove(temp_input_path)  # чистим оригинал

    # 4. Нарезаем на куски ровно по 10 секунд
    i = 0
    while i < usable_duration:
        start_time = i
        output_filename = os.path.join(chunks_dir, f"asmr_{i//10:03d}.mp4")

        cut_chunk_command = [
            'ffmpeg', '-y', '-i', trimmed_path,
            '-ss', str(start_time),
            '-t', '10',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-an',
            output_filename
        ]
        subprocess.run(cut_chunk_command, check=True)
        i += 10

    os.remove(trimmed_path)  # удаляем обрезанное видео

    # 5. Обработка кусков
    for filename in sorted(os.listdir(chunks_dir)):
        if filename.startswith('asmr_') and filename.endswith('.mp4'):
            chunk_path = os.path.join(chunks_dir, filename)

            # Проверка длины каждого куска
            chunk_duration_command = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                chunk_path
            ]
            chunk_duration = float(subprocess.check_output(chunk_duration_command).decode().strip())

            if chunk_duration < 9.5:  # подстраховка
                os.remove(chunk_path)
                continue

            # Обработка видео
            temp_processed_path = os.path.join(chunks_dir, f'processed_{filename}')
            randomize_video(chunk_path, temp_processed_path)

            # Сохраняем в БД
            dummy_file = "asmr/temp.mp4"
            asmr_record = ASMR.objects.create(file=dummy_file)

            # Формируем финальное имя
            final_filename = f'asmr{asmr_record.id}.mp4'
            final_ready_path = os.path.join(ready_dir, final_filename)

            shutil.move(temp_processed_path, final_ready_path)

            relative_ready_path = os.path.relpath(final_ready_path, settings.MEDIA_ROOT)
            asmr_record.file = relative_ready_path
            asmr_record.save()

            os.remove(chunk_path)
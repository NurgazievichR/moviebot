import random
import subprocess

def randomize_video(input_path, output_path):
    """Рандомная переработка видео с обязательным флипом и без аудио"""

    crop_scale = round(random.uniform(0.8, 0.95), 2)   # Обрезка 80–95%
    brightness = round(random.uniform(-0.05, 0.1), 2)  # Яркость от -0.05 до +0.1
    contrast = round(random.uniform(0.9, 1.2), 2)      # Контраст от 0.9 до 1.2
    speed = round(random.uniform(0.9, 1.1), 2)         # Скорость 0.9–1.1
    hue = random.randint(-20, 20)                      # Оттенок от -20 до +20

    # Список обязательных фильтров
    filters = [
        f"crop=iw*{crop_scale}:ih*{crop_scale}",
        "hflip",  # Всегда флип
        f"eq=brightness={brightness}:contrast={contrast}",
        f"setpts={1/speed}*PTS",
        f"hue=h={hue}:s=1",
    ]

    filter_chain = ",".join(filters)

    command = [
        'ffmpeg',
        '-i', input_path,
        '-vf', filter_chain,
        '-an',  # ВСЕГДА убираем звук
        '-preset', 'fast',
        output_path
    ]

    # print("Running command:", " ".join(command))

    subprocess.run(command, check=True)

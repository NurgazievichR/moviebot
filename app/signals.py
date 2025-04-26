from django.db.models.signals import post_delete
from django.dispatch import receiver
import os

from .models import ASMR  
from django.conf import settings

@receiver(post_delete, sender=ASMR)
def delete_asmr_file(sender, instance, **kwargs):
    """Удаляет файл с диска, когда удаляется запись ASMR."""
    if instance.file:
        file_path = os.path.join(settings.MEDIA_ROOT, str(instance.file))
        if os.path.isfile(file_path):
            os.remove(file_path)
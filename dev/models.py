from django.db import models

class FormatSettings(models.Model):
    allowed_extensions = models.TextField(help_text="Перечисли допустимые расширения через пробел, например: mp4 mov webm")

    def get_allowed_list(self):
        """Вернёт список расширений."""
        if not self.allowed_extensions:
            return []
        return [ext.strip().lower() for ext in self.allowed_extensions.split()]

    def __str__(self):
        return "Настройки допустимых форматов"
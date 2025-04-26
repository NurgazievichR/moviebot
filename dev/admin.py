from django.contrib import admin
from .models import FormatSettings

@admin.register(FormatSettings)
class FormatSettingsAdmin(admin.ModelAdmin):
    list_display = ('allowed_extensions_display',)
    readonly_fields = ('allowed_extensions_display',)

    def allowed_extensions_display(self, obj):
        """Красиво показывать список расширений в столбце."""
        return ", ".join(obj.get_allowed_list())

    allowed_extensions_display.short_description = "Допустимые расширения"

    def has_add_permission(self, request):
        """Разрешить добавление только если нет ни одной записи."""
        if FormatSettings.objects.exists():
            return False
        return super().has_add_permission(request)

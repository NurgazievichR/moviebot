from django.contrib import admin
from .models import ASMR, Project, ProjectFile
from .tasks import process_video 

@admin.action(description='Запустить обработку видео через Celery')
def start_video_processing(modeladmin, request, queryset):
    for project_file in queryset:
        process_video.delay(project_file.id) 
        print('gere')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at', 'status')


    #все поля нельзя менять
    def get_readonly_fields(self, request, obj=None):
        readonly = []
        if obj: 
            readonly.append('file')
            readonly.append('status')
            readonly.append('project')
            readonly.append('uploaded_at')
        return readonly

    #статус нельзя выбирать при создании
    def get_exclude(self, request, obj=None):
        if obj is None:  
            return ('status',)
        return ()
    
    actions = [start_video_processing]  

@admin.register(ASMR)   
class ASMRAdmin(admin.ModelAdmin):
    fields = ('file', 'created_at')

    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj = ...):
        return False
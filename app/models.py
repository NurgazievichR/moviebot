from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='projects/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('uploaded', 'Uploaded'),
            ('processing', 'Processing'),
            ('ready', 'Ready'),
            ('uploaded_to_tiktok', 'Uploaded to TikTok'),
        ],
        default='uploaded'
    )

    def __str__(self):
        return self.file.name

class ASMR(models.Model):
    file = models.FileField(upload_to='asmr/chunks/')
    created_at = models.DateTimeField(auto_now_add=True)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_files, name='upload_files'),
    path('asmr/', views.upload_asmr, name='upload_asmr'),
]


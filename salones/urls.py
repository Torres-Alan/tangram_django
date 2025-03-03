# salones/urls.py
from django.urls import path, include

app_name = 'salones'

urlpatterns = [
    path('api/', include('salones.api.urls')),  # Aquí estamos incluyendo las URLs de la API de salones
]

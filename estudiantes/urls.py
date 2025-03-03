# salones/urls.py
from django.urls import path, include

app_name = 'estudiantes'

urlpatterns = [
    path('api/', include('estudiantes.api.urls')),  # Aquí estamos incluyendo las URLs de la API de salones
]

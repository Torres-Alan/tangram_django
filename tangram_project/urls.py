# mysite/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('maestros.urls')),
    path('', include('salones.urls')),
    path('', include('estudiantes.urls')),
]

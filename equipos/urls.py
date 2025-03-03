from django.urls import path, include
from . import views

app_name="equipos"

urlpatterns = [
    path('api/', include('equipos.api.urls')),
]
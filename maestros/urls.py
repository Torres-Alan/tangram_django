from django.urls import path, re_path, include
from . import views

app_name="maestros"

urlpatterns = [
    path('api/', include('maestros.api.urls')),
]
# salones/apps.py
from django.apps import AppConfig

class SalonesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # Especifica el tipo de campo auto generado para claves primarias
    name = 'salones'  # Nombre de la aplicación, que debe coincidir con el nombre de la carpeta de la aplicación

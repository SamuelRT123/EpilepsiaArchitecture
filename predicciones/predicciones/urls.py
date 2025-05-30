# Si este es el urls.py principal del proyecto, asegúrate de incluir:
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('manejador_prediccion.urls')),  # Reemplaza 'tu_app' con el nombre de tu aplicación
    # Otras rutas de autenticación si las tienes configuradas
]
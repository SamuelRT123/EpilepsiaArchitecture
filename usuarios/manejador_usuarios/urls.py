# manejador_usuarios/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.saludo, name='saludo'),
    path('usuarios/ver-todos', views.mostrar_usuarios, name='ver_todos_usuarios'),
    path('usuarios/crear', views.crear_usuario, name='crear_usuario'),

]

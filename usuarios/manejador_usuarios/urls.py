from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.saludo, name='home'),
    path(r'^usuarios/', views.saludo, name='saludo'),
    path('usuarios/ver-todos', views.mostrar_usuarios, name='ver_todos_usuarios'),
    path('usuarios/crear', views.crear_usuario, name='crear_usuario'),
    path('logout/auth0/', views.logout_auth0, name='logout_auth0'),  # Nueva línea
    path(r'', include('django.contrib.auth.urls')),
]
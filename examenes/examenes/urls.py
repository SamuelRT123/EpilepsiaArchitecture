"""examenes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, url

from manejador_examenes import views

urlpatterns = [
    url(r'^examenes/', views.saludo),
    path('admin/', admin.site.urls),
    path('subir_examen/', views.subir_examen_eeg, name='subir_examen'),
    path('ver_examenes/', views.ver_examenes_eeg, name='ver_examenes'),
    path('', include('manejador_examenes.urls')),
]

from django.shortcuts import render, redirect
from django.http import HttpResponse

from . import authBackend  
from .models import Usuario
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
import requests
import json
from django.contrib.auth.decorators import login_required


from django.shortcuts import redirect
from urllib.parse import urlencode

from django.contrib.auth import logout
from django.shortcuts import redirect
from urllib.parse import urlencode

def health_check(request):
    return HttpResponse("OK")
    

def logout_auth0(request):
    """Logout personalizado para Auth0"""
    # Cerrar sesión en Django
    logout(request)
    
    # Construir URL de logout de Auth0
    domain = settings.SOCIAL_AUTH_AUTH0_DOMAIN
    client_id = settings.SOCIAL_AUTH_AUTH0_KEY
    return_to = request.build_absolute_uri('/')  # URL a donde regresar después del logout
    
    logout_url = f'https://{domain}/v2/logout?' + urlencode({
        'client_id': client_id,
        'returnTo': return_to
    })
    
    return redirect(logout_url)

@login_required
def UsuariosList(request):
    role= authBackend.getRole(request)
    if role == "Medico":
        queryset = Usuario.objects.all()
        context = list(queryset.values('id', 'variable', 'value', 'unit', 'place', 'dateTime'))
        return JsonResponse(context, safe=False)

def saludo(request):
    return render(request, 'manejador_usuarios/base.html')

#@login_required
def mostrar_usuarios(request):
    role = authBackend.getRole(request)
    role = "Medico"
    if role == "Medico":
        usuarios = Usuario.objects.all()
        return render(request, 'manejador_usuarios/usuarios_lista.html', {'usuarios': usuarios})
    else:
        # Manejar usuarios que no son médicos
        messages.error(request, 'No tienes permisos para ver esta página. Solo los médicos pueden acceder.')
        return redirect('home')  # O redirigir a donde consideres apropiado
    
@login_required
def crear_usuario(request):
    role = authBackend.getRole(request)
    if role == "Medico":
        if request.method == 'POST':
            nombre = request.POST.get('nombre')
            activo = request.POST.get('activo') == 'on'
            fecha_ingreso = request.POST.get('fecha_ingreso')
            fecha_estimada_salida = request.POST.get('fecha_estimada_salida')

            nuevo_usuario = Usuario(
                nombre=nombre,
                activo=activo,
                fecha_ingreso=fecha_ingreso,
                fecha_estimada_salida=fecha_estimada_salida,
                examenes_ids=[] 
            )
            nuevo_usuario.save()
            return redirect('ver_todos_usuarios')

        return render(request, 'manejador_usuarios/crear_usuario.html')
    
    else:
        # Manejar usuarios que no son médicos
        messages.error(request, 'No tienes permisos para ver esta página. Solo los médicos pueden acceder.')
        return redirect('home')  # O redirigir a donde consideres apropiado
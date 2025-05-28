from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Usuario
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
import requests
import json

def check_variable(data):
    r = requests.get(settings.PATH_VAR, headers={"Accept":"application/json"})
    variables = r.json()
    for variable in variables:
        if data["variable"] == variable["id"]:
            return True
    return False

def UsuariosList(request):
    queryset = Usuario.objects.all()
    context = list(queryset.values('id', 'variable', 'value', 'unit', 'place', 'dateTime'))
    return JsonResponse(context, safe=False)

def saludo(request):
    return render(request, 'manejador_usuarios/base.html')

def mostrar_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'manejador_usuarios/usuarios_lista.html', {'usuarios': usuarios})
    

def crear_usuario(request):
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

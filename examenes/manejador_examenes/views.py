from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import EEGRecord
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
import requests
from pymongo import MongoClient
from bson import ObjectId
import json
from django.views.decorators.csrf import csrf_exempt


def check_usuario(data):
    r = requests.get(settings.PATH_VAR, headers={"Accept":"application/json"})
    usuarios = r.json()
    for usuario in usuarios:
        if data["paciente"]["nombre"] == usuario["nombre"]:
            return True
    return False

def ver_examenes_eeg(request):
    client = MongoClient(settings.MONGO_CLI)
    db = client.eeg_db
    eeg_collection = db['eeg_records']

    # Traer todos los exámenes
    examenes = list(eeg_collection.find())

    # Convertir ObjectId a string para usar en plantillas
    for ex in examenes:
        ex['_id'] = str(ex['_id'])

    client.close()

    return render(request, 'manejador_examenes/ver_examenes_eeg.html', {'examenes': examenes})


def saludo(request):
    return render(request, 'manejador_examenes/base.html')


def createEEGRecord(data):
    # Validar y convertir a objeto EEGRecord
    eeg_record = EEGRecord.from_dict(data)

    client = MongoClient(settings.MONGO_CLI)
    db = client.eeg_db

    # Verificar que el paciente existe en la colección 'pacientes'
    pacientes_collection = db['pacientes']
    paciente_db = pacientes_collection.find_one({'_id': ObjectId(eeg_record.paciente.id)})
    
    if paciente_db is None:
        raise ValueError("Paciente no encontrado en la base de datos")

    # Preparar documento para insertar (convierte el objeto EEGRecord a dict)
    # Aquí simplificamos convirtiendo manualmente, pero se puede hacer mejor con métodos to_dict en las clases.
    doc = {
        "paciente": {
            "id": eeg_record.paciente.id,
            "nombre": eeg_record.paciente.nombre,
            "edad": eeg_record.paciente.edad,
            "sexo": eeg_record.paciente.sexo,
            "historial_medico": {
                "epilepsia": eeg_record.paciente.historial_medico.epilepsia,
                "medicacion": eeg_record.paciente.historial_medico.medicacion,
                "otros_diagnosticos": eeg_record.paciente.historial_medico.otros_diagnosticos,
            }
        },
        "examen": {
            "id": eeg_record.examen.id,
            "fecha": eeg_record.examen.fecha.isoformat(),
            "duracion_segundos": eeg_record.examen.duracion_segundos,
            "frecuencia_muestreo": eeg_record.examen.frecuencia_muestreo,
            "electrodos": eeg_record.examen.electrodos,
            "sistema_colocacion": eeg_record.examen.sistema_colocacion,
            "filtros_aplicados": {
                "notch": eeg_record.examen.filtros_aplicados.notch,
                "pasa_alto": eeg_record.examen.filtros_aplicados.pasa_alto,
                "pasa_bajo": eeg_record.examen.filtros_aplicados.pasa_bajo,
            }
        },
        "datos": [
            {"tiempo": d.tiempo, "valores": d.valores}
            for d in eeg_record.datos
        ],
        "eventos": [
            {
                "tipo": e.tipo,
                "canal": e.canal,
                "canales": e.canales,
                "tiempo": e.tiempo,
                "tiempo_inicio": e.tiempo_inicio,
                "tiempo_fin": e.tiempo_fin,
                "amplitud": e.amplitud,
                "frecuencia_dominante": e.frecuencia_dominante,
                "descripcion": e.descripcion,
                "nivel_ruido": e.nivel_ruido,
                "frecuencia": e.frecuencia
            }
            for e in eeg_record.eventos
        ],
        "analisis": {
            "espectro_frecuencial": {
                canal: {
                    "delta": ef.delta,
                    "theta": ef.theta,
                    "alpha": ef.alpha,
                    "beta": ef.beta,
                    "gamma": ef.gamma
                }
                for canal, ef in eeg_record.analisis.espectro_frecuencial.items()
            },
            "sincronizacion_canal": eeg_record.analisis.sincronizacion_canal
        }
    }

    eeg_collection = db['eeg_records']
    result = eeg_collection.insert_one(doc)

    # Guardamos el ObjectId asignado en el objeto
    eeg_record.id = str(result.inserted_id)

    client.close()
    return eeg_record



@csrf_exempt
def subir_examen_eeg(request):
    if request.method == 'POST':
        if 'archivo_json' not in request.FILES:
            return JsonResponse({'error': 'No se proporcionó un archivo JSON'}, status=400)

        archivo = request.FILES['archivo_json']
        if not archivo.name.endswith('.json'):
            return JsonResponse({'error': 'El archivo debe ser un .json'}, status=400)

        try:
            contenido = archivo.read().decode('utf-8')
            data = json.loads(contenido)
            eeg_record = createEEGRecord(data)
        except Exception as e:
            return JsonResponse({'error': f'Error procesando el archivo: {str(e)}'}, status=500)

        return JsonResponse({'mensaje': 'Examen EEG subido correctamente', 'id': eeg_record.id}, status=200)

    return render(request, 'manejador_examenes/subir_examen_eeg.html')

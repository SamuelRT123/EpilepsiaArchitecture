from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import requests
from pymongo import MongoClient
from bson import ObjectId
import json
import os  # ← IMPORT AGREGADO


def check_usuario(data):
    #return True
    r = requests.get(settings.PATH_USER, headers={"Accept":"application/json"})
    usuarios = r.json()
    for usuario in usuarios:
        if data["paciente"]["nombre"] == usuario["nombre"]:
            return True
    return False

def ver_examenes_eeg(request):
    examenes = []
    error_message = None
    
    try:
        print("Intentando conectar a MongoDB...")  # Debug
      
        client = MongoClient(settings.MONGO_CLI, serverSelectionTimeoutMS=5000)  # 5 segundos timeout
        
        # Probar la conexión
        client.admin.command('ping')
        print("Conexión a MongoDB exitosa")  # Debug
        
        db = client.eeg_db
        eeg_collection = db['eeg_records']

        # Traer todos los exámenes
        examenes = list(eeg_collection.find())
        print(f"Se encontraron {len(examenes)} exámenes")  # Debug

        # Convertir ObjectId a string y cambiar el nombre del campo para los templates
        for ex in examenes:
            ex['id'] = str(ex['_id'])  # Crear campo 'id' sin guión bajo
            del ex['_id']  # Eliminar el campo original

        client.close()
        
    except Exception as e:
        error_message = f"Error al conectar con la base de datos: {str(e)}"
        print(f"Error MongoDB: {error_message}")  # Debug
        examenes = []

    return render(request, 'manejador_examenes/ver_examenes_eeg.html', {
        'examenes': examenes,
        'error_message': error_message
    })


def saludo(request):
    return render(request, 'manejador_examenes/base.html')


def save_eeg_to_mongodb(datos_json):
    
    # Validar que el usuario existe usando check_usuario
    if not check_usuario(datos_json):
        raise ValueError(f"El paciente '{datos_json['paciente']['nombre']}' no existe en el sistema")
    
    client = MongoClient(settings.MONGO_CLI)
    db = client.eeg_db
    eeg_collection = db['eeg_records']
    
    try:
        # Insertar el JSON después de validar el usuario
        result = eeg_collection.insert_one(datos_json)
        client.close()
        return str(result.inserted_id)
    except Exception as e:
        client.close()
        raise e


@csrf_exempt
@require_http_methods(["GET", "POST"])
def subir_examen_eeg(request):
    if request.method == 'POST':
        print("POST request recibido")  # Debug
        print("FILES:", request.FILES)  # Debug
        
        # Verificar que se haya enviado un archivo
        if 'archivo_json' not in request.FILES:
            return JsonResponse({
                'success': False, 
                'error': 'No se seleccionó ningún archivo'
            })
        
        archivo = request.FILES['archivo_json']
        print(f"Archivo recibido: {archivo.name}")  # Debug
        
        # Verificar que el archivo tenga extensión .json
        if not archivo.name.endswith('.json'):
            return JsonResponse({
                'success': False, 
                'error': 'El archivo debe tener extensión .json'
            })
        
        try:
            # Leer y validar el contenido JSON
            contenido = archivo.read().decode('utf-8')
            datos_json = json.loads(contenido)
            print("JSON parseado correctamente")  # Debug
            
            # Validaciones específicas para la estructura de tu JSON EEG
            campos_requeridos = ['paciente', 'examen', 'datos']
            for campo in campos_requeridos:
                if campo not in datos_json:
                    return JsonResponse({
                        'success': False, 
                        'error': f'El archivo JSON debe contener el campo: {campo}'
                    })
            
            # Validar estructura del paciente
            if 'id' not in datos_json['paciente']:
                return JsonResponse({
                    'success': False, 
                    'error': 'El campo "paciente" debe contener un "id"'
                })
            
            # Validar estructura del examen
            campos_examen = ['id', 'fecha', 'electrodos']
            for campo in campos_examen:
                if campo not in datos_json['examen']:
                    return JsonResponse({
                        'success': False, 
                        'error': f'El campo "examen" debe contener: {campo}'
                    })
            
            # Crear directorio si no existe
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'examenes_eeg')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Guardar archivo con nombre único
            paciente_id = datos_json['paciente']['id']
            examen_id = datos_json['examen']['id']
            nombre_archivo = f"examen_{paciente_id}_{examen_id}.json"
            ruta_archivo = os.path.join(upload_dir, nombre_archivo)
            
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(datos_json, f, indent=2, ensure_ascii=False)
            
            print(f"Archivo guardado en: {ruta_archivo}")  # Debug
            
            # NUEVO: Guardar también en MongoDB
            try:
                mongodb_id = save_eeg_to_mongodb(datos_json)
                print(f"Guardado en MongoDB con ID: {mongodb_id}")
            except ValueError as validation_error:
                # Error de validación de usuario
                return JsonResponse({
                    'success': False, 
                    'error': str(validation_error)
                })
            except Exception as mongo_error:
                print(f"Error al guardar en MongoDB: {str(mongo_error)}")
                return JsonResponse({
                    'success': False, 
                    'error': f'Error al guardar en base de datos: {str(mongo_error)}'
                })
            
            return JsonResponse({
                'success': True, 
                'message': f'Archivo {archivo.name} subido exitosamente',
                'archivo': nombre_archivo
            })
            
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False, 
                'error': f'El archivo no contiene JSON válido: {str(e)}'
            })
        except Exception as e:
            print(f"Error: {str(e)}")  # Debug
            return JsonResponse({
                'success': False, 
                'error': f'Error al procesar el archivo: {str(e)}'
            })
    
    # GET request - mostrar la página principal
    print("GET request recibido")  # Debug
    return render(request, 'manejador_examenes/subir_examen_eeg.html')
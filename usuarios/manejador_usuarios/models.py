from django.db import models
from django.contrib.postgres.fields import JSONField

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    fecha_ingreso = models.CharField(max_length=30)
    fecha_estimada_salida = models.CharField(max_length=30)

    # # Lista de IDs de exámenes (guardados como enteros separados por coma)
    examenes_ids = models.TextField(blank=True, default="")

    def __str__(self):
        return self.nombre
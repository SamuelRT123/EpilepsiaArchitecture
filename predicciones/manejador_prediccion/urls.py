
# urls.py de tu aplicación
from django.urls import path
from . import views

urlpatterns = [
    path('', views.prediccion_view, name='home'),
    path('prediccion/', views.prediccion_view, name='prediccion_view'),
    path('api/prediccion/', views.api_prediccion, name='api_prediccion'),
]

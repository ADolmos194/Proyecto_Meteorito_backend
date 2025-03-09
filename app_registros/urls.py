from django.views.decorators.csrf import csrf_exempt
from django.conf.urls.static import static
from django.conf import settings
from django.template.defaulttags import url
from django.urls import path

from .views import *

# Definición de las rutas URL para la API de clientes
urlpatterns = [
    # Ruta para listar todos los clientes
    path('clientes/', listar_clientes, name="listar_clientes"),

    # Ruta para crear un nuevo cliente
    path('clientes/crear/', crear_cliente, name="crear_cliente"),

    # Ruta para actualizar un cliente existente, identificando el cliente por su ID
    path('clientes/actualizar/<int:id>/', actualizar_cliente, name="actualizar_cliente"),

    # Ruta para eliminar un cliente (cambiar su estado a 'eliminado') por su ID
    path('clientes/eliminar/<int:id>/', eliminar_cliente, name="eliminar_cliente"),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

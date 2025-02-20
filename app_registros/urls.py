from django.views.decorators.csrf import csrf_exempt
from django.conf.urls.static import static
from django.conf import settings
from django.template.defaulttags import url
from django.urls import path

from .views import *

urlpatterns = [ 
            
    path('clientes/', listar_clientes, name="listar_clientes"),
    path('clientes/crear/', crear_cliente, name="crear_cliente"),
    path('clientes/actualizar/<int:id>/', actualizar_cliente, name="actualizar_cliente"),
    path('clientes/eliminar/<int:id>/', eliminar_cliente, name="eliminar_cliente"),
    
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
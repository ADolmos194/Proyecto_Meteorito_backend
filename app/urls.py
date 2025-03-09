from django.views.decorators.csrf import csrf_exempt
from django.conf.urls.static import static
from django.conf import settings
from django.template.defaulttags import url
from django.urls import path



# Importación de las vistas que serán utilizadas en las URLs
from .views import *


# Definición de las URLs de la aplicación
urlpatterns = [
    
    # Ruta para listar los estados. Asociado con la vista 'listar_estado' 
    path('estado/', listar_estado, name="listar_estado"),
    
    
    # Ruta para listar los tipos de documento. Asociado con la vista 'listar_tipodocumento'
    path('tipodocumento/', listar_tipodocumento, name="listar_tipodocumento"),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
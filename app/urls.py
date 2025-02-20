from django.views.decorators.csrf import csrf_exempt
from django.conf.urls.static import static
from django.conf import settings
from django.template.defaulttags import url
from django.urls import path

from .views import *

urlpatterns = [ 
    path('estado/', listar_estado, name="listar_estado"),
    path('tipodocumento/', listar_tipodocumento, name="listar_tipodocumento"),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
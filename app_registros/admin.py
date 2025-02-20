from django.contrib import admin

from app_registros.models import *

# Register your models here.
admin.site.register([Clientes, Tesis, Pagos])
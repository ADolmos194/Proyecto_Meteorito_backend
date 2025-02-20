from rest_framework import serializers
from .models import (
    Clientes, 
    )




################################################## GENERAL ############################################################
class ClientesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clientes
        fields = '__all__' 
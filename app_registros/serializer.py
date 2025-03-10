from rest_framework import serializers
from .models import (
    Clientes, Tesis
    )

################################################## GENERAL ############################################################
class ClientesSerializer(serializers.ModelSerializer):
    
    """
    Serializer para el modelo Clientes. Este serializer se utiliza para convertir 
    los objetos de tipo Cliente en representaciones JSON y viceversa.
    Permite la validación y serialización de datos de clientes en las vistas de la API.

    Utiliza todos los campos del modelo Clientes.
    """
    
    class Meta:
        # Define el modelo que se va a serializar
        model = Clientes
        
        # Incluye todos los campos del modelo en la serialización
        fields = '__all__' 
        
class TesisSerializer(serializers.ModelSerializer):
    
    class Meta:
        
        model = Tesis
        
        fields = '__all__'
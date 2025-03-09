from django.db import models

# Modelo que representa un Estado
class Estado(models.Model):

    """
    El modelo Estado representa una entidad que almacena el nombre de un estado o condición.
    Este modelo se puede utilizar en sistemas donde se requiera clasificar o almacenar estados 
    de objetos o procesos, como estados de órdenes, productos, etc.
    """
    # Campo para almacenar el nombre del estado
    nombre = models.CharField(max_length=25, null=True, blank=True)
    
    # Fecha de creación automática del registro
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Fecha de última modificación automática del registro
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        # Define el nombre de la tabla en la base de datos
        db_table = "estado"
        
    def __str__(self):
        
        """
        Método que devuelve una representación en cadena del modelo.
        En este caso, devuelve el nombre del estado.
        """
        return '%s' % (self.nombre)

#Es eso aplica en el resto de los modelos
class Tipodocumento(models.Model):

    nombre = models.CharField(max_length=25, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tipodocumento"
        
    def __str__(self):
	    return '%s' % (self.nombre)

class Formapago(models.Model):

    nombre = models.CharField(max_length=25, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Formapago"
        
    def __str__(self):
	    return '%s' % (self.nombre)
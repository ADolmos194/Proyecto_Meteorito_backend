from django.db import models

# Create your models here.
class Estado(models.Model):

    nombre = models.CharField(max_length=25, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "estado"
        
    def __str__(self):
	        return '%s' % (self.nombre)

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
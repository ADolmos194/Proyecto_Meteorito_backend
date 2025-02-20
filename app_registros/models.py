from django.db import models
from app.models import  Estado, Formapago, Tipodocumento

class Clientes(models.Model):
    
    tipodocumento = models.ForeignKey(Tipodocumento, on_delete=models.CASCADE)
    nro_documento = models.CharField(max_length=15, null=True, blank=True)
    nombre_completo = models.CharField(max_length=100, null=True, blank=True)
    correo_electronico = models.CharField(max_length=255, null=True, blank=True)
    nro_celular = models.CharField(max_length=25, null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "clientes"
        
    def __str__(self):
	    return '%s' % (self.nombre_completo)

class Tesis(models.Model):
    
    clientes = models.ForeignKey(Clientes, on_delete=models.CASCADE)
    tesis = models.CharField(max_length=255, null=True, blank=True)
    universidad = models.CharField(max_length=100, null=True, blank=True)
    usuario_plataforma = models.CharField(max_length=25, null=True, blank=True)
    clave_plataforma = models.CharField(max_length=25, null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "tesis"
        
    def __str__(self):
	    return '%s' % (self.tesis)

class Pagos(models.Model):
    
    clientes = models.ForeignKey(Clientes, on_delete=models.CASCADE)
    tesis = models.CharField(max_length=255, null=True, blank=True)
    formapago = models.ForeignKey(Formapago, on_delete=models.CASCADE)
    monto_completo = models.CharField(max_length=100, null=True, blank=True)
    cantidad_cuotas = models.CharField(max_length=100, null=True, blank=True)
    monto_cuotas = models.CharField(max_length=100, null=True, blank=True)
    cuotas_cancelado = models.CharField(max_length=100, null=True, blank=True)
    monto_cancelado = models.CharField(max_length=100, null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "pagos"
        
    def __str__(self):
	    return '%s' % (self.monto_completo)


from django.db import models
from django.utils import timezone
from datetime import timedelta

class Producto(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    destacado = models.BooleanField(default=False)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nombre

class ClienteAnonimo(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, default='invitado')
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"



class Pedido(models.Model):
    id = models.IntegerField(primary_key=True, default=1)  # Campo ID personalizado
    direccion = models.CharField(max_length=200, default="Dirección Desconocida")
    cliente_anonimo = models.ForeignKey(ClienteAnonimo, on_delete=models.CASCADE, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    METODO_PAGO_CHOICES = (
        ('efectivo', 'Efectivo'),
        ('mercado_pago', 'Mercado Pago'),
    )
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='efectivo')
    comprobante_pago = models.ImageField(upload_to='comprobantes/', null=True, blank=True)
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    def __str__(self):
        return f"Pedido #{self.id}"

    def actualizar_total(self):
        total = sum(item.cantidad * item.precio_unitario for item in self.itempedido_set.all())
        self.total = total
        self.save()

    @property
    def puede_eliminar(self):
        ahora = timezone.now()
        tiempo_transcurrido = ahora - self.fecha_creacion
        return tiempo_transcurrido < timedelta(minutes=5)

    def save(self, *args, **kwargs):
        if not self.id:  # Si no hay ID, es un nuevo pedido
            last_pedido = Pedido.objects.order_by('-id').first()
            if last_pedido:
                self.id = last_pedido.id + 1
            else:
                if not Pedido.objects.filter(id=1).exists(): #agregado
                    self.id = 1
                else:
                    last_pedido = Pedido.objects.order_by('-id').first()
                    self.id = last_pedido.id + 1

        super().save(*args, **kwargs) 

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Pedido #{self.pedido.id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.pedido.actualizar_total()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.pedido.actualizar_total()

   
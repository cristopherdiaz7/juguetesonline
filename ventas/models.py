from django.db import models

# Create your models here.
    
from django.db import models

class Usuario(models.Model):
    TIPO_CHOICES = [
        ('comprador', 'Comprador'),
        ('vendedor', 'Vendedor'),
    ]

    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=100) 
    direccion = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    descripcion = models.TextField()
    stock = models.IntegerField()

    def __str__(self):
        return self.nombre

class CarritoDeCompras(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Carrito #{self.id} de {self.usuario.nombre}"

class CarritoProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    carrito = models.ForeignKey(CarritoDeCompras, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('producto', 'carrito')

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en carrito #{self.carrito.id}"

class Pedido(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=50)

    def __str__(self):
        return f"Pedido #{self.id} de {self.usuario.nombre}"

class Pago(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)
    metodo_de_pago = models.CharField(max_length=50)
    estado = models.CharField(max_length=50)

    def __str__(self):
        return f"Pago #{self.id} - {self.metodo_de_pago}"

class Envio(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    direccion = models.TextField()
    empresa_envio = models.CharField(max_length=100)
    estado = models.CharField(max_length=50)

    def __str__(self):
        return f"Envío #{self.id} - {self.empresa_envio}"

class Reseña(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    comentario = models.TextField()
    calificacion = models.IntegerField()

    def __str__(self):
        return f"Reseña de {self.usuario.nombre} para {self.producto.nombre}"


from rest_framework import viewsets
from .serializer import (
    UsuarioSerializer,
    ProductoSerializer,
    CarritoDeComprasSerializer,
    CarritoProductoSerializer,
    PedidoSerializer,
    PagoSerializer,
    EnvioSerializer,
    ReseñaSerializer
)
from .models import Usuario, Producto, CarritoDeCompras, CarritoProducto, Pedido, Pago, Envio, Reseña

class UsuarioView(viewsets.ModelViewSet):
    serializer_class = UsuarioSerializer
    queryset = Usuario.objects.all()

class ProductoView(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer
    queryset = Producto.objects.all()

class CarritoDeComprasView(viewsets.ModelViewSet):
    serializer_class = CarritoDeComprasSerializer
    queryset = CarritoDeCompras.objects.all()

class CarritoProductoView(viewsets.ModelViewSet):
    serializer_class = CarritoProductoSerializer
    queryset = CarritoProducto.objects.all()

class PedidoView(viewsets.ModelViewSet):
    serializer_class = PedidoSerializer
    queryset = Pedido.objects.all()

class PagoView(viewsets.ModelViewSet):
    serializer_class = PagoSerializer
    queryset = Pago.objects.all()

class EnvioView(viewsets.ModelViewSet):
    serializer_class = EnvioSerializer
    queryset = Envio.objects.all()

class ReseñaView(viewsets.ModelViewSet):
    serializer_class = ReseñaSerializer
    queryset = Reseña.objects.all()

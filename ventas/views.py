from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from .models import *
from .serializer import *

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Leer sin autenticación, modificar con autenticación

class CarritoDeComprasViewSet(viewsets.ModelViewSet):
    queryset = CarritoDeCompras.objects.all()
    serializer_class = CarritoDeComprasSerializer
    permission_classes = [IsAuthenticated]

class CarritoProductoViewSet(viewsets.ModelViewSet):
    queryset = CarritoProducto.objects.all()
    serializer_class = CarritoProductoSerializer
    permission_classes = [IsAuthenticated]

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]

class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]

class EnvioViewSet(viewsets.ModelViewSet):
    queryset = Envio.objects.all()
    serializer_class = EnvioSerializer
    permission_classes = [IsAuthenticated]

class ReseñaViewSet(viewsets.ModelViewSet):
    queryset = Reseña.objects.all()
    serializer_class = ReseñaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Leer sin autenticación, crear con autenticación


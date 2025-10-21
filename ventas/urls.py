from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'carritos', CarritoDeComprasViewSet)
router.register(r'carrito-productos', CarritoProductoViewSet)
router.register(r'pedidos', PedidoViewSet)
router.register(r'pagos', PagoViewSet)
router.register(r'envios', EnvioViewSet)
router.register(r'resenas', ReseñaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

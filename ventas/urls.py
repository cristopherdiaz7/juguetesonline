from django.urls import path, include
from rest_framework import routers
from ventas import views

router = routers.DefaultRouter()

router.register(r'usuarios', views.UsuarioView, basename='usuarios')
router.register(r'productos', views.ProductoView, basename='productos')
router.register(r'carritos', views.CarritoDeComprasView, basename='carritos')
router.register(r'carrito_productos', views.CarritoProductoView, basename='carrito_productos')
router.register(r'pedidos', views.PedidoView, basename='pedidos')
router.register(r'pago', views.PagoView, basename='pago')
router.register(r'envios', views.EnvioView, basename='envios')
router.register(r'reseñas', views.ReseñaView, basename='reseñas')

urlpatterns = [
    path('dualcash/model', include(router.urls)),
]


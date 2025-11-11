from django.contrib import admin
from .models import (
    Usuario,
    Producto,
    CarritoDeCompras,
    CarritoProducto,
    Pedido,
    Pago,
    Envio,
    Reseña
)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'correo', 'tipo')
    search_fields = ('nombre', 'correo')
    list_filter = ('tipo',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio', 'stock', 'usuario', 'imagen_tag')
    search_fields = ('nombre',)
    list_filter = ('usuario',)

    def imagen_tag(self, obj):
        if getattr(obj, 'imagen', None):
            return f"<img src='{obj.imagen.url}' style='max-height:50px; max-width:100px;'/>"
        return '-'
    imagen_tag.short_description = 'Imagen'
    imagen_tag.allow_tags = True

@admin.register(CarritoDeCompras)
class CarritoDeComprasAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha')
    list_filter = ('fecha',)

@admin.register(CarritoProducto)
class CarritoProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'carrito', 'producto', 'cantidad', 'precio')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha', 'total', 'estado')
    list_filter = ('estado',)

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'monto', 'metodo_de_pago', 'estado')
    list_filter = ('metodo_de_pago', 'estado')

@admin.register(Envio)
class EnvioAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'empresa_envio', 'estado')
    list_filter = ('empresa_envio', 'estado')

@admin.register(Reseña)
class ReseñaAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto', 'usuario', 'calificacion')
    list_filter = ('calificacion',)
    search_fields = ('producto__nombre', 'usuario__nombre')


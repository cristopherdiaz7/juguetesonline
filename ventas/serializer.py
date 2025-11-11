from rest_framework import serializers
from django.db import transaction
from .models import *

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    # Expose imagen as a URL when available (DRF will use request to build full URL)
    imagen = serializers.ImageField(use_url=True, allow_null=True, required=False)

    class Meta:
        model = Producto
        fields = '__all__'

class CarritoDeComprasSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarritoDeCompras
        fields = '__all__'

class CarritoProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarritoProducto
        fields = '__all__'

class PedidoSerializer(serializers.ModelSerializer):
    # `usuario` should be read-only: the API user is determined from the authenticated request
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)
    usuario_nombre = serializers.SerializerMethodField(read_only=True)
    # permitir enviar items al crear un pedido
    items = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)
    # exponer items en la respuesta
    items_out = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'usuario', 'usuario_nombre', 'fecha', 'total', 'estado', 'items', 'items_out']

    def get_usuario_nombre(self, obj):
        try:
            return getattr(obj.usuario, 'nombre', str(obj.usuario))
        except Exception:
            return None

    def get_items_out(self, obj):
        try:
            from .models import PedidoItem
            items = PedidoItem.objects.filter(pedido=obj)
            return [{'producto_id': it.producto.id if it.producto else None, 'nombre': (it.producto.nombre if it.producto else 'Producto eliminado'), 'cantidad': it.cantidad, 'precio': float(it.precio)} for it in items]
        except Exception:
            return []

    def create(self, validated_data):
        items = validated_data.pop('items', [])
        request = self.context.get('request')
        # determinar el usuario ventas (modelo ventas.Usuario) asociado al request.user
        ventas_user = None
        try:
            if request and getattr(request, 'user', None) and request.user.is_authenticated:
                from .models import Usuario as VentasUsuario
                django_user = request.user
                # Try to find by nombre or correo first
                ventas_user = VentasUsuario.objects.filter(nombre=django_user.username).first()
                if not ventas_user and getattr(django_user, 'email', None):
                    ventas_user = VentasUsuario.objects.filter(correo=django_user.email).first()
                # If still not found, create a new ventas Usuario with a guaranteed-unique email
                if not ventas_user:
                    unique_email = getattr(django_user, 'email', None) or f"{django_user.username}@local.invalid"
                    # ensure unique email by appending suffix if needed
                    base_email = unique_email
                    counter = 0
                    while VentasUsuario.objects.filter(correo=unique_email).exists():
                        counter += 1
                        unique_email = f"{django_user.username}+{counter}@local.invalid"
                    ventas_user = VentasUsuario.objects.create(
                        nombre=django_user.username,
                        correo=unique_email,
                        contraseña='',
                        direccion=(getattr(django_user, 'direccion', '') if hasattr(django_user, 'direccion') else ''),
                        tipo='comprador'
                    )
        except Exception:
            ventas_user = None

        # calcular total si no fue enviado
        total = validated_data.get('total')
        if total in (None, ''):
            total_calc = 0
            for it in items:
                precio = float(it.get('precio', it.get('price', 0) or 0))
                cantidad = int(it.get('cantidad', it.get('quantity', 1) or 1))
                total_calc += precio * cantidad
            total = total_calc
        validated_data['total'] = total

        # crear Pedido (necesitamos un usuario de ventas válido)
        if ventas_user is None:
            from rest_framework import serializers as drf_serializers
            raise drf_serializers.ValidationError({'usuario': 'No se pudo asociar un usuario de ventas para este pedido.'})

        # Hacer la creación atómica: si falla la persistencia de items o el stock no alcanza, revertir todo
        from rest_framework import serializers as drf_serializers
        from .models import Producto, PedidoItem
        try:
                # Do NOT decrement stock at order creation time.
                # Validate requested quantities against current stock so buyers cannot order more than available.
                with transaction.atomic():
                    pedido = Pedido.objects.create(usuario=ventas_user, total=total, estado=validated_data.get('estado', 'pendiente'))

                    # create PedidoItem(s) that belong to this pedido, but do NOT modify Producto.stock here.
                    for it in items:
                        try:
                            prod = Producto.objects.get(pk=it.get('id') or it.get('producto_id'))
                        except Producto.DoesNotExist:
                            prod = None

                        cantidad = int(it.get('cantidad', it.get('quantity', 1) or 1))
                        precio = float(it.get('precio', it.get('price', getattr(prod, 'precio', 0) if prod else 0) or 0))

                        # if we have a product, validate stock availability but do not decrement yet
                        if prod is not None:
                            if prod.stock is None:
                                prod.stock = 0
                            if prod.stock <= 0:
                                # explicitly tell the client this product is out of stock
                                raise drf_serializers.ValidationError({'items': f'stock insuficiente (para {prod.nombre}). disponible ({prod.stock}), solicitado ({cantidad})'})
                            if prod.stock < cantidad:
                                # inform client that requested quantity exceeds available stock
                                raise drf_serializers.ValidationError({'items': f'stock insuficiente (para {prod.nombre}). disponible ({prod.stock}), solicitado ({cantidad})'})

                        PedidoItem.objects.create(pedido=pedido, producto=prod, cantidad=cantidad, precio=precio)

        except drf_serializers.ValidationError:
            # propagar errores de validación (por ejemplo stock insuficiente)
            raise
        except Exception:
            # Si ocurre otro error, convertir a ValidationError para que el cliente lo reciba
            raise drf_serializers.ValidationError({'items': 'Error al crear los items del pedido.'})

        # crear Envio si se envió shipping en request.data
        try:
            shipping = request.data.get('shipping') if request is not None else None
            if shipping:
                from .models import Envio
                direccion = shipping.get('direccion', '')
                ciudad = shipping.get('ciudad', '')
                telefono = shipping.get('telefono', '')
                full_dir = f"{direccion}, {ciudad}. Tel: {telefono}"
                Envio.objects.create(pedido=pedido, direccion=full_dir, empresa_envio='', estado='pendiente')
        except Exception:
            pass

        # crear una notificación para el usuario indicando que el pedido fue creado y está pendiente
        try:
            from .models import Notification
            Notification.objects.create(usuario=ventas_user, message=f'Tu pedido {pedido.id} fue creado y está pendiente.', tipo='info')
        except Exception:
            pass

        return pedido

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'

class EnvioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Envio
        fields = '__all__'

class ReseñaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reseña
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = getattr(__import__(__name__.split('.')[0] + '.models', fromlist=['Notification']), 'Notification')
        fields = ['id', 'usuario', 'usuario_nombre', 'message', 'tipo', 'read', 'created_at']

    def get_usuario_nombre(self, obj):
        try:
            return getattr(obj.usuario, 'nombre', str(obj.usuario))
        except Exception:
            return None

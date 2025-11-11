from rest_framework import viewsets
from .models import *
from .serializer import *
from .permissions import IsAdminOrReadOnly, AllowAuthenticatedNonAdminOrReadOnly, OrderPermissionForAdminAndOwner
from rest_framework import permissions as drf_permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=True, methods=['post'], permission_classes=[drf_permissions.IsAdminUser], url_path='upload_image')
    def upload_image(self, request, pk=None):
        """Upload an image file for this product. Admin-only.

        Endpoint: POST /api/productos/{pk}/upload_image/ with multipart form-data 'imagen'
        """
        try:
            producto = self.get_object()
        except Exception:
            return Response({'detail': 'Producto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        file_obj = request.FILES.get('imagen')
        if not file_obj:
            return Response({'detail': 'No se envió el archivo `imagen`.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            producto.imagen.save(file_obj.name, file_obj, save=True)
            serializer = self.get_serializer(producto)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': f'Error al guardar la imagen: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        """Allow filtering by ?categoria=<slug> from the frontend. Defaults to all products."""
        qs = super().get_queryset()
        try:
            # Apply category filter if provided
            categoria = self.request.query_params.get('categoria')
            if categoria:
                qs = qs.filter(categoria__iexact=categoria)

            # For non-admin viewers (buyers / anonymous) hide products marked as OLD -
            request = getattr(self, 'request', None)
            user = getattr(request, 'user', None) if request is not None else None
            is_admin = bool(getattr(user, 'is_staff', False))
            if not is_admin:
                qs = qs.exclude(nombre__istartswith='OLD - ')
        except Exception:
            # On error, fall back to returning all non-OLD products
            try:
                return super().get_queryset().exclude(nombre__istartswith='OLD - ')
            except Exception:
                return super().get_queryset()
        return qs

class CarritoDeComprasViewSet(viewsets.ModelViewSet):
    queryset = CarritoDeCompras.objects.all()
    serializer_class = CarritoDeComprasSerializer
    # Allow reads for everyone, but only authenticated NON-admins can create/update carts
    permission_classes = [AllowAuthenticatedNonAdminOrReadOnly]

class CarritoProductoViewSet(viewsets.ModelViewSet):
    queryset = CarritoProducto.objects.all()
    serializer_class = CarritoProductoSerializer
    # Prevent admins from adding items to carts via API; only authenticated buyers can write
    permission_classes = [AllowAuthenticatedNonAdminOrReadOnly]

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    # Buyers can POST orders, admins can PATCH/PUT to change status (see permission implementation)
    permission_classes = [OrderPermissionForAdminAndOwner]

    def update(self, request, *args, **kwargs):
        """
        Override update so that when an admin changes a Pedido's estado we
        - on transition to 'aprobado': decrement stock for the pedido items transactionally (fail the update if stock insufficient)
        - on transition from 'aprobado' to 'rechazado' (or other non-aprobado): restore stock for the items that were previously decremented
        - otherwise, behave like a normal update
        Also create a Notification for the pedido owner when admin changes estado.
        """
        instance = self.get_object()
        estado_before = instance.estado
        requested_estado = request.data.get('estado', None)

        # if no estado change or requester isn't admin, fall back to default update behavior
        if not (requested_estado is not None and getattr(request, 'user', None) and request.user.is_staff and requested_estado != estado_before):
            return super().update(request, *args, **kwargs)

        # We have an admin-requested estado change
        from django.db import transaction
        from .models import Producto, PedidoItem, Notification
        # Approve path: decrement stocks transactionally, but fail if any stock insufficient
        if requested_estado == 'aprobado':
            try:
                with transaction.atomic():
                    items = PedidoItem.objects.select_related('producto').filter(pedido=instance)
                    # collect product ids to lock
                    prod_ids = [it.producto_id for it in items if it.producto_id]
                    prods = {p.id: p for p in Producto.objects.select_for_update().filter(id__in=prod_ids)}

                    # validate availability
                    for it in items:
                        prod = prods.get(it.producto_id)
                        if prod is None:
                            # if product was deleted, treat as unavailable
                            return Response({'detail': f'Producto eliminado en el pedido (item id {it.id}). No se puede aprobar.'}, status=status.HTTP_400_BAD_REQUEST)
                        if prod.stock is None:
                            prod.stock = 0
                        if prod.stock < it.cantidad:
                            # prettier alert format requested by user
                            return Response({'detail': f'stock insuficiente (para {prod.nombre}). disponible ({prod.stock}), solicitado ({it.cantidad})'}, status=status.HTTP_400_BAD_REQUEST)

                    # decrement stocks
                    for it in items:
                        prod = prods.get(it.producto_id)
                        prod.stock -= it.cantidad
                        prod.save()

                    # now perform the state change
                    instance.estado = requested_estado
                    instance.save()

                    # create notification for user
                    try:
                        msg = f'Tu pedido {instance.id} fue aprobado.'
                        Notification.objects.create(usuario=instance.usuario, message=msg, tipo='success')
                    except Exception:
                        pass

                    serializer = self.get_serializer(instance)
                    return Response(serializer.data)
            except Exception as e:
                return Response({'detail': f'Error al aprobar pedido: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Rechazar path: if previously aprobado, restore stock; then set estado to requested
        elif requested_estado == 'rechazado':
            try:
                with transaction.atomic():
                    if estado_before == 'aprobado':
                        items = PedidoItem.objects.select_related('producto').filter(pedido=instance)
                        prod_ids = [it.producto_id for it in items if it.producto_id]
                        prods = {p.id: p for p in Producto.objects.select_for_update().filter(id__in=prod_ids)}
                        for it in items:
                            prod = prods.get(it.producto_id)
                            if prod is None:
                                continue
                            prod.stock = (prod.stock or 0) + it.cantidad
                            prod.save()

                    # set estado and save
                    instance.estado = requested_estado
                    instance.save()

                    # notification
                    try:
                        msg = f'Tu pedido {instance.id} fue rechazado.'
                        Notification.objects.create(usuario=instance.usuario, message=msg, tipo='danger')
                    except Exception:
                        pass

                    serializer = self.get_serializer(instance)
                    return Response(serializer.data)
            except Exception as e:
                return Response({'detail': f'Error al rechazar pedido: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Other estado transitions: just apply them
        else:
            # reuse serializer to update other fields
            return super().update(request, *args, **kwargs)

class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer

class EnvioViewSet(viewsets.ModelViewSet):
    queryset = Envio.objects.all()
    serializer_class = EnvioSerializer

class ReseñaViewSet(viewsets.ModelViewSet):
    queryset = Reseña.objects.all()
    serializer_class = ReseñaSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = getattr(__import__(__name__.split('.')[0] + '.models', fromlist=['Notification']), 'Notification').objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return notifications for the ventas.Usuario associated with the authenticated request.user
        request = self.request
        qs = super().get_queryset()
        try:
            if request and getattr(request, 'user', None) and request.user.is_authenticated:
                # map Django user to ventas.Usuario similarly to how PedidoSerializer does
                from .models import Usuario as VentasUsuario
                django_user = request.user
                ventas_user = VentasUsuario.objects.filter(nombre=django_user.username).first()
                if not ventas_user and getattr(django_user, 'email', None):
                    ventas_user = VentasUsuario.objects.filter(correo=django_user.email).first()
                if ventas_user:
                    return qs.filter(usuario=ventas_user)
        except Exception:
            pass
        return qs.none()

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        try:
            from .models import Usuario as VentasUsuario
            django_user = request.user
            ventas_user = VentasUsuario.objects.filter(nombre=django_user.username).first()
            if not ventas_user and getattr(django_user, 'email', None):
                ventas_user = VentasUsuario.objects.filter(correo=django_user.email).first()
            if not ventas_user:
                return Response({'detail': 'No se pudo asociar el usuario de ventas.'}, status=status.HTTP_400_BAD_REQUEST)
            from .models import Notification
            updated = Notification.objects.filter(usuario=ventas_user, read=False).update(read=True)
            return Response({'updated': updated})
        except Exception:
            return Response({'detail': 'Error marcando notificaciones.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

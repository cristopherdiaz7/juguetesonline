from rest_framework import generics, permissions
from rest_framework.permissions import IsAdminUser
from .models import Usuario
from .serializer import UsuarioSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import transaction
from ventas.models import Usuario as VentasUsuario

# Vistas para CRUD de Usuario usando DRF
class UsuarioListView(generics.ListCreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    # Sólo los administradores pueden listar usuarios; cualquiera puede registrarse (POST)
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.AllowAny()]
        # GET (list) y otros métodos de lectura/edición requieren ser admin
        return [IsAdminUser()]

class UsuarioDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.user.is_staff:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]



@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)  # Django guarda la sesión y la cookie
                return JsonResponse({'message': 'Login correcto'})
            else:
                return JsonResponse({'error': 'Usuario o contraseña incorrectos'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


# Vista para logout
@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logout correcto'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# Vista para registro (registro de nuevos usuarios)
@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email', '')
            tipo = data.get('tipo', 'comprador')  # Valor por defecto
            direccion = data.get('direccion', '')

            if not username or not password:
                return JsonResponse({'error': 'Username y password son requeridos'}, status=400)

            if Usuario.objects.filter(username=username).exists():
                return JsonResponse({'error': 'El usuario ya existe'}, status=400)

            # Crear ambos registros en una transacción: Django auth (useradmin.Usuario)
            # y la tabla legada de ventas (ventas.Usuario) duplicando el hash de contraseña.
            with transaction.atomic():
                usuario = Usuario.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    tipo=tipo,
                    direccion=direccion
                )

                # La tabla de ventas espera campos: nombre, correo, contraseña, direccion, tipo
                # Algunos registros antiguos almacenaban la contraseña hasheada en formato Django.
                ventas_correo = email if email else f"{username}@no-email.local"
                # Guardar el hash generado por Django en el campo 'contraseña' de ventas
                VentasUsuario.objects.create(
                    nombre=username,
                    correo=ventas_correo,
                    contraseña=usuario.password,
                    direccion=direccion or '',
                    tipo=tipo
                )

            return JsonResponse({'message': 'Usuario creado correctamente'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


# Endpoint para obtener datos del usuario autenticado
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    # Debug: log the Authorization header and user for troubleshooting
    # debug prints removed
    serializer = UsuarioSerializer(request.user)
    data = serializer.data
    return Response(data)


# Endpoint para cambiar contraseña del usuario autenticado
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    try:
        current = request.data.get('current_password')
        new = request.data.get('new_password')
        if not current or not new:
            return Response({'error': 'current_password and new_password are required'}, status=400)

        user = request.user
        if not user.check_password(current):
            return Response({'error': 'Current password is incorrect'}, status=400)

        # Optionally enforce password validation rules here
        user.set_password(new)
        user.save()
        return Response({'message': 'Password changed successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


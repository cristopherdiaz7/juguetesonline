from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Usuario
from .serializer import UsuarioSerializer

class UsuarioListView(generics.ListCreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class UsuarioDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    tipo = request.data.get('tipo', 'comprador')
    direccion = request.data.get('direccion', '')

    if not username or not password:
        return Response(
            {'error': 'Username y password son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if Usuario.objects.filter(username=username).exists():
        return Response(
            {'error': 'El usuario ya existe'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usuario = Usuario.objects.create_user(
            username=username,
            password=password,
            email=email,
            tipo=tipo,
            direccion=direccion
        )
        return Response({
            'message': 'Usuario registrado correctamente',
            'user': {
                'id': usuario.id,
                'username': usuario.username,
                'email': usuario.email,
                'tipo': usuario.tipo
            },
            'instrucciones': 'Usa POST /api/token/ para obtener tu token JWT'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

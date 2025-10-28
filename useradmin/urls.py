# useradmin/urls.py

from django.urls import path
from .views import register_view, UsuarioListView, UsuarioDetailView

urlpatterns = [
    # Registro de usuarios (público)
    path('register/', register_view, name='register'),
    # CRUD de usuarios (requiere autenticación JWT)
    path('usuarios/', UsuarioListView.as_view(), name='usuario-list'),
    path('usuarios/<int:pk>/', UsuarioDetailView.as_view(), name='usuario-detail'),
]

# NOTA: Los endpoints de login/logout ya no son necesarios.
# Para autenticarse, usar: POST /api/token/ con username y password.
# Para refrescar el token, usar: POST /api/token/refresh/ con el refresh token.



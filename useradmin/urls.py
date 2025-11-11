# useradmin/urls.py

from django.urls import path
from .views import login_view, logout_view, register_view, UsuarioListView, UsuarioDetailView, me_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('me/', me_view, name='me'),
    path('usuarios/', UsuarioListView.as_view(), name='usuario-list'),
    path('usuarios/<int:pk>/', UsuarioDetailView.as_view(), name='usuario-detail'),
]


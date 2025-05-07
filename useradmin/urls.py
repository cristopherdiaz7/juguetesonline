from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('vendedor-dashboard/', views.vendedor_dashboard, name='vendedor_dashboard'),
    path('comprador-dashboard/', views.comprador_dashboard, name='comprador_dashboard'),
]

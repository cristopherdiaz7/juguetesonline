# useradmin/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse

# Vista de Login
def login_view(request):
    if request.method == 'POST':
        # Usamos el formulario de autenticación estándar de Django
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            # Si las credenciales son correctas, logueamos al usuario
            usuario = form.get_user()
            login(request, usuario)

            # Redirigimos dependiendo del tipo de usuario
            if usuario.tipo == 'vendedor':
                return redirect('vendedor_dashboard')  # Redirige al dashboard de vendedor
            elif usuario.tipo == 'comprador':
                return redirect('comprador_dashboard')  # Redirige al dashboard de comprador
        else:
            # Si el formulario no es válido, mostramos el error
            return render(request, 'useradmin/login.html', {'form': form, 'error': 'Credenciales incorrectas'})
    else:
        form = AuthenticationForm()

    return render(request, 'useradmin/login.html', {'form': form})

# Vista para el Dashboard del Vendedor
def vendedor_dashboard(request):
    return HttpResponse("Panel de control del vendedor")

# Vista para el Dashboard del Comprador
def comprador_dashboard(request):
    return HttpResponse("Panel de control del comprador")

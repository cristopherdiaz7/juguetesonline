"""
TP5 - Pruebas de funcionalidades API con JWT
Tests actualizados para usar autenticación JWT en lugar de cookies de sesión.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from ventas.models import Producto, CarritoDeCompras, CarritoProducto, Pedido, Usuario as VentasUsuario
from useradmin.models import Usuario as AdminUsuario


class JWTAuthTestCase(TestCase):
    """
    Clase base para tests con autenticación JWT.
    Proporciona métodos helper para obtener tokens.
    """
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()
        
    def create_user(self, username, password, email='test@example.com', tipo='comprador'):
        """Helper para crear usuarios en useradmin (para JWT)"""
        return AdminUsuario.objects.create_user(
            username=username,
            password=password,
            email=email,
            tipo=tipo,
            direccion='Calle Test 123'
        )
    
    def create_ventas_user(self, nombre, correo, tipo='comprador'):
        """Helper para crear usuarios en ventas (para relaciones FK)"""
        return VentasUsuario.objects.create(
            nombre=nombre,
            correo=correo,
            contraseña='dummy',
            direccion='Calle Test 123',
            tipo=tipo
        )
    
    def get_tokens(self, username, password):
        """
        Helper para obtener tokens JWT de un usuario.
        Retorna un dict con 'access' y 'refresh' tokens.
        """
        response = self.client.post('/api/token/', {
            'username': username,
            'password': password
        }, format='json')
        
        if response.status_code == 200:
            return response.data
        return None
    
    def authenticate(self, username, password):
        """
        Helper para autenticar el cliente con JWT.
        Configura el header Authorization automáticamente.
        """
        tokens = self.get_tokens(username, password)
        if tokens:
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
            return tokens
        return None


class FuncionalidadesAPIJWTTests(JWTAuthTestCase):
    """
    Suite de pruebas para las 6 funcionalidades principales con JWT:
    1. Registro de usuarios
    2. Login de usuarios (obtener token JWT)
    3. Agregado de productos (con autenticación)
    4. Listado de productos (sin autenticación)
    5. Agregar producto al carrito (con autenticación)
    6. Crear pedido desde el carrito (con autenticación)
    """

    def test_1_registro_usuario(self):
        """
        Test 1: Registro de usuarios
        Verifica que un nuevo usuario pueda registrarse mediante la API.
        """
        datos_usuario = {
            "username": "usuario_nuevo",
            "password": "mipass123",
            "email": "nuevo@example.com",
            "tipo": "comprador",
            "direccion": "Av. Nueva 456"
        }
        
        response = self.client.post('/api/user/register/', datos_usuario, format='json')
        
        # Verificar que la respuesta sea exitosa
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que el usuario se creó en la BD (usando el campo correcto)
        self.assertTrue(AdminUsuario.objects.filter(email="nuevo@example.com").exists())
        
        # Verificar los datos del usuario creado
        usuario_creado = AdminUsuario.objects.get(email="nuevo@example.com")
        self.assertEqual(usuario_creado.username, "usuario_nuevo")
        self.assertEqual(usuario_creado.tipo, "comprador")

    def test_2_login_usuario_jwt(self):
        """
        Test 2: Login de usuarios con JWT
        Verifica que un usuario pueda obtener tokens JWT válidos.
        """
        # Crear un usuario de prueba
        username = "usuario_login"
        password = "pass123"
        self.create_user(username, password, email="login@test.com")
        
        # Intentar obtener tokens
        response = self.client.post('/api/token/', {
            'username': username,
            'password': password
        }, format='json')
        
        # Verificar que la respuesta sea exitosa
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que se reciban ambos tokens
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Verificar que los tokens no estén vacíos
        self.assertTrue(len(response.data['access']) > 0)
        self.assertTrue(len(response.data['refresh']) > 0)

    def test_3_agregado_producto_con_jwt(self):
        """
        Test 3: Agregado de productos (con autenticación JWT)
        Verifica que un vendedor autenticado pueda registrar productos.
        """
        # Crear vendedor en admin (para JWT) y en ventas (para FK)
        self.create_user('vendedor_test', 'pass123', tipo='vendedor')
        vendedor_ventas = self.create_ventas_user('Vendedor Test', 'vendedor@test.com', tipo='vendedor')
        self.authenticate('vendedor_test', 'pass123')
        
        # Crear producto
        datos_producto = {
            "nombre": "Funko Pop Batman JWT",
            "precio": "2500.00",
            "usuario": vendedor_ventas.id,
            "descripcion": "Figura coleccionable con JWT",
            "stock": 10
        }
        
        response = self.client.post('/api/productos/', datos_producto, format='json')
        
        # Verificar que la respuesta sea exitosa
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que el producto se creó
        self.assertTrue(Producto.objects.filter(nombre="Funko Pop Batman JWT").exists())

    def test_4_listado_productos_sin_auth(self):
        """
        Test 4: Listado de productos (sin autenticación)
        Verifica que el endpoint de listado sea público (IsAuthenticatedOrReadOnly).
        """
        # Crear un vendedor y un producto (sin autenticar el cliente)
        vendedor = self.create_ventas_user('Vendedor Público', 'vendedor_publico@test.com', tipo='vendedor')
        Producto.objects.create(
            nombre="Producto Público",
            precio=1000.00,
            usuario=vendedor,
            descripcion="Visible sin autenticación",
            stock=5
        )
        
        # Intentar listar productos SIN autenticación
        self.client.credentials()  # Limpiar credenciales
        response = self.client.get('/api/productos/')
        
        # Verificar que la respuesta sea exitosa
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que retorne una lista
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)

    def test_5_agregar_producto_al_carrito_con_jwt(self):
        """
        Test 5: Agregar producto al carrito (con autenticación JWT)
        Verifica que un usuario autenticado pueda agregar productos a su carrito.
        """
        # Crear vendedor y producto
        vendedor = self.create_ventas_user('Vendedor Carrito', 'vendedor_carrito@test.com', tipo='vendedor')
        producto = Producto.objects.create(
            nombre="Producto para Carrito JWT",
            precio=800.00,
            usuario=vendedor,
            descripcion="Producto de prueba JWT",
            stock=20
        )
        
        # Crear comprador en ambos sistemas y autenticar
        self.create_user('comprador_jwt', 'pass123', tipo='comprador')
        comprador_ventas = self.create_ventas_user('Comprador JWT', 'comprador_jwt@test.com', tipo='comprador')
        self.authenticate('comprador_jwt', 'pass123')
        
        # Crear carrito
        carrito = CarritoDeCompras.objects.create(usuario=comprador_ventas)
        
        # Agregar producto al carrito
        datos_carrito_producto = {
            "producto": producto.id,
            "carrito": carrito.id,
            "cantidad": 2,
            "precio": str(producto.precio)
        }
        
        response = self.client.post(
            '/api/carrito-productos/',
            datos_carrito_producto,
            format='json'
        )
        
        # Verificar que la respuesta sea exitosa
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que el producto se agregó al carrito
        carrito_producto = CarritoProducto.objects.filter(
            carrito=carrito,
            producto=producto
        ).first()
        
        self.assertIsNotNone(carrito_producto)
        self.assertEqual(carrito_producto.cantidad, 2)

    def test_6_crear_pedido_con_jwt(self):
        """
        Test 6: Crear pedido desde el carrito (con autenticación JWT)
        Verifica que se genere correctamente un pedido con autenticación JWT.
        """
        # Crear vendedor y productos
        vendedor = self.create_ventas_user('Vendedor Pedido', 'vendedor_pedido@test.com', tipo='vendedor')
        producto1 = Producto.objects.create(
            nombre="Producto Pedido JWT 1",
            precio=500.00,
            usuario=vendedor,
            descripcion="Para pedido JWT",
            stock=10
        )
        
        # Crear comprador en ambos sistemas y autenticar
        self.create_user('comprador_pedido_jwt', 'pass123', tipo='comprador')
        comprador_ventas = self.create_ventas_user('Comprador Pedido JWT', 'comprador_pedido_jwt@test.com', tipo='comprador')
        self.authenticate('comprador_pedido_jwt', 'pass123')
        
        # Crear carrito con productos
        carrito = CarritoDeCompras.objects.create(usuario=comprador_ventas)
        CarritoProducto.objects.create(
            carrito=carrito,
            producto=producto1,
            cantidad=2,
            precio=producto1.precio
        )
        
        # Crear pedido
        total_esperado = 1000.00  # 500 * 2
        datos_pedido = {
            "usuario": comprador_ventas.id,
            "total": str(total_esperado),
            "estado": "pendiente"
        }
        
        response = self.client.post('/api/pedidos/', datos_pedido, format='json')
        
        # Verificar que la respuesta sea exitosa
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que el pedido se generó correctamente
        pedido = Pedido.objects.filter(usuario=comprador_ventas).first()
        self.assertIsNotNone(pedido)
        self.assertEqual(float(pedido.total), total_esperado)

    def test_7_acceso_sin_token_falla(self):
        """
        Test 7: Verificar que endpoints protegidos rechacen requests sin token
        """
        # Intentar crear un pedido SIN autenticación
        self.client.credentials()  # Limpiar credenciales
        
        datos_pedido = {
            "usuario": 1,
            "total": "1000.00",
            "estado": "pendiente"
        }
        
        response = self.client.post('/api/pedidos/', datos_pedido, format='json')
        
        # Verificar que se rechace (401 Unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_8_token_refresh(self):
        """
        Test 8: Verificar que se pueda refrescar un token
        """
        # Crear usuario y obtener tokens
        self.create_user('usuario_refresh', 'pass123')
        tokens = self.get_tokens('usuario_refresh', 'pass123')
        
        self.assertIsNotNone(tokens)
        
        # Usar el refresh token para obtener un nuevo access token
        response = self.client.post('/api/token/refresh/', {
            'refresh': tokens['refresh']
        }, format='json')
        
        # Verificar que se obtenga un nuevo access token
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertTrue(len(response.data['access']) > 0)

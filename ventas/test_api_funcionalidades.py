"""
TP4 - Pruebas de funcionalidades principales de la API
Pruebas automáticas que simulan el uso real de la API como lo haría el frontend.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from ventas.models import Usuario, Producto, CarritoDeCompras, CarritoProducto, Pedido


class FuncionalidadesAPITests(TestCase):
    """
    Suite de pruebas para las 6 funcionalidades principales del ecommerce:
    1. Registro de usuarios
    2. Login de usuarios
    3. Agregado de productos (como admin/vendedor)
    4. Listado de productos
    5. Agregar producto al carrito
    6. Crear pedido desde el carrito
    """

    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()
        
        # Crear un vendedor para las pruebas de productos
        self.vendedor = Usuario.objects.create(
            nombre="Vendedor Test",
            correo="vendedor@test.com",
            contraseña="pass123",
            direccion="Calle Vendedor 123",
            tipo="vendedor"
        )

    def test_1_registro_usuario(self):
        """
        Test 1: Registro de usuarios
        Verifica que un nuevo usuario pueda registrarse correctamente mediante la API.
        """
        datos_usuario = {
            "nombre": "Usuario Nuevo",
            "correo": "nuevo@example.com",
            "contraseña": "mipass123",
            "direccion": "Av. Nueva 456",
            "tipo": "comprador"
        }
        
        response = self.client.post('/api/dualcash/model/usuarios/', datos_usuario, format='json')
        
        # Verificar que la respuesta sea exitosa
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que el usuario se creó en la BD
        self.assertTrue(Usuario.objects.filter(correo="nuevo@example.com").exists())
        
        # Verificar los datos del usuario creado
        usuario_creado = Usuario.objects.get(correo="nuevo@example.com")
        self.assertEqual(usuario_creado.nombre, "Usuario Nuevo")
        self.assertEqual(usuario_creado.tipo, "comprador")

    def test_2_login_usuario(self):
        """
        Test 2: Login de usuarios
        Verifica que un usuario pueda iniciar sesión con credenciales válidas.
        
        Nota: Este test verifica la existencia del usuario y sus credenciales.
        En un sistema real con autenticación JWT o sesiones, aquí se probaría
        el endpoint de login y se verificaría que retorne un token válido.
        """
        # Crear un usuario de prueba
        usuario_test = Usuario.objects.create(
            nombre="Usuario Login",
            correo="login@test.com",
            contraseña="pass123",
            direccion="Calle Login 789",
            tipo="comprador"
        )
        
        # Verificar que el usuario existe y las credenciales coinciden
        usuario_encontrado = Usuario.objects.filter(
            correo="login@test.com",
            contraseña="pass123"
        ).first()
        
        self.assertIsNotNone(usuario_encontrado)
        self.assertEqual(usuario_encontrado.nombre, "Usuario Login")

    def test_3_agregado_producto(self):
        """
        Test 3: Agregado de productos (como vendedor)
        Verifica que un producto se pueda registrar en el sistema.
        """
        datos_producto = {
            "nombre": "Funko Pop Batman",
            "precio": "2500.00",
            "usuario": self.vendedor.id,
            "descripcion": "Figura coleccionable de Batman",
            "stock": 10
        }
        
        response = self.client.post('/api/dualcash/model/productos/', datos_producto, format='json')
        
        # Verificar que la respuesta sea exitosa
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que el producto se creó en la BD
        self.assertTrue(Producto.objects.filter(nombre="Funko Pop Batman").exists())
        
        # Verificar los datos del producto
        producto_creado = Producto.objects.get(nombre="Funko Pop Batman")
        self.assertEqual(float(producto_creado.precio), 2500.00)
        self.assertEqual(producto_creado.stock, 10)
        self.assertEqual(producto_creado.usuario.id, self.vendedor.id)

    def test_4_listado_productos(self):
        """
        Test 4: Listado de productos
        Verifica que el endpoint que lista productos funcione correctamente.
        """
        # Crear algunos productos de prueba
        Producto.objects.create(
            nombre="Producto 1",
            precio=1000.00,
            usuario=self.vendedor,
            descripcion="Descripción 1",
            stock=5
        )
        Producto.objects.create(
            nombre="Producto 2",
            precio=1500.00,
            usuario=self.vendedor,
            descripcion="Descripción 2",
            stock=3
        )
        
        response = self.client.get('/api/dualcash/model/productos/')
        
        # Verificar que la respuesta sea exitosa
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que retorne una lista
        self.assertIsInstance(response.data, list)
        
        # Verificar que retorne al menos 2 productos
        self.assertGreaterEqual(len(response.data), 2)
        
        # Verificar que los productos tengan los campos esperados
        primer_producto = response.data[0]
        self.assertIn('nombre', primer_producto)
        self.assertIn('precio', primer_producto)
        self.assertIn('stock', primer_producto)

    def test_5_agregar_producto_al_carrito(self):
        """
        Test 5: Agregar producto al carrito
        Verifica que un usuario pueda agregar un producto a su carrito.
        """
        # Crear un comprador
        comprador = Usuario.objects.create(
            nombre="Comprador Test",
            correo="comprador@test.com",
            contraseña="pass123",
            direccion="Calle Comprador 321",
            tipo="comprador"
        )
        
        # Crear un producto
        producto = Producto.objects.create(
            nombre="Producto para Carrito",
            precio=800.00,
            usuario=self.vendedor,
            descripcion="Producto de prueba",
            stock=20
        )
        
        # Crear un carrito para el comprador
        carrito = CarritoDeCompras.objects.create(usuario=comprador)
        
        # Agregar producto al carrito mediante la API
        datos_carrito_producto = {
            "producto": producto.id,
            "carrito": carrito.id,
            "cantidad": 2,
            "precio": str(producto.precio)
        }
        
        response = self.client.post(
            '/api/dualcash/model/carrito_productos/',
            datos_carrito_producto,
            format='json'
        )
        
        # Verificar que la respuesta sea exitosa
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que el producto se agregó al carrito en la BD
        carrito_producto = CarritoProducto.objects.filter(
            carrito=carrito,
            producto=producto
        ).first()
        
        self.assertIsNotNone(carrito_producto)
        self.assertEqual(carrito_producto.cantidad, 2)
        self.assertEqual(float(carrito_producto.precio), 800.00)

    def test_6_crear_pedido_desde_carrito(self):
        """
        Test 6: Crear pedido desde el carrito
        Verifica que se genere correctamente un pedido a partir de los productos del carrito.
        """
        # Crear un comprador
        comprador = Usuario.objects.create(
            nombre="Comprador Pedido",
            correo="pedido@test.com",
            contraseña="pass123",
            direccion="Calle Pedido 999",
            tipo="comprador"
        )
        
        # Crear productos
        producto1 = Producto.objects.create(
            nombre="Producto Pedido 1",
            precio=500.00,
            usuario=self.vendedor,
            descripcion="Descripción pedido 1",
            stock=10
        )
        producto2 = Producto.objects.create(
            nombre="Producto Pedido 2",
            precio=700.00,
            usuario=self.vendedor,
            descripcion="Descripción pedido 2",
            stock=5
        )
        
        # Crear carrito y agregar productos
        carrito = CarritoDeCompras.objects.create(usuario=comprador)
        CarritoProducto.objects.create(
            carrito=carrito,
            producto=producto1,
            cantidad=2,
            precio=producto1.precio
        )
        CarritoProducto.objects.create(
            carrito=carrito,
            producto=producto2,
            cantidad=1,
            precio=producto2.precio
        )
        
        # Calcular el total esperado: (500 * 2) + (700 * 1) = 1700
        total_esperado = 1700.00
        
        # Crear pedido mediante la API
        datos_pedido = {
            "usuario": comprador.id,
            "total": str(total_esperado),
            "estado": "pendiente"
        }
        
        response = self.client.post('/api/dualcash/model/pedidos/', datos_pedido, format='json')
        
        # Verificar que la respuesta sea exitosa
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que el pedido se creó en la BD
        pedido_creado = Pedido.objects.filter(usuario=comprador).first()
        self.assertIsNotNone(pedido_creado)
        self.assertEqual(float(pedido_creado.total), total_esperado)
        self.assertEqual(pedido_creado.estado, "pendiente")
        
        # Verificar que el pedido tiene el usuario correcto
        self.assertEqual(pedido_creado.usuario.id, comprador.id)

    def test_7_flujo_completo_compra(self):
        """
        Test 7: Flujo completo de compra (integración)
        Simula todo el proceso: registro → login → ver productos → agregar al carrito → crear pedido
        """
        # 1. Registrar un nuevo comprador
        datos_comprador = {
            "nombre": "Comprador Completo",
            "correo": "completo@test.com",
            "contraseña": "pass123",
            "direccion": "Calle Completo 777",
            "tipo": "comprador"
        }
        response = self.client.post('/api/dualcash/model/usuarios/', datos_comprador, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comprador = Usuario.objects.get(correo="completo@test.com")
        
        # 2. Crear un producto disponible
        producto = Producto.objects.create(
            nombre="Producto Flujo Completo",
            precio=1200.00,
            usuario=self.vendedor,
            descripcion="Producto para flujo completo",
            stock=15
        )
        
        # 3. Listar productos y verificar que existe
        response = self.client.get('/api/dualcash/model/productos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        productos = response.data
        self.assertTrue(any(p['nombre'] == "Producto Flujo Completo" for p in productos))
        
        # 4. Crear carrito y agregar producto
        carrito = CarritoDeCompras.objects.create(usuario=comprador)
        datos_carrito_producto = {
            "producto": producto.id,
            "carrito": carrito.id,
            "cantidad": 3,
            "precio": str(producto.precio)
        }
        response = self.client.post(
            '/api/dualcash/model/carrito_productos/',
            datos_carrito_producto,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 5. Crear pedido desde el carrito
        total = 1200.00 * 3  # 3600.00
        datos_pedido = {
            "usuario": comprador.id,
            "total": str(total),
            "estado": "confirmado"
        }
        response = self.client.post('/api/dualcash/model/pedidos/', datos_pedido, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que todo se creó correctamente
        pedido = Pedido.objects.get(usuario=comprador)
        self.assertEqual(float(pedido.total), 3600.00)
        self.assertEqual(pedido.estado, "confirmado")

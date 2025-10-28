from django.test import TestCase
from ventas.models import Usuario, Producto
from ventas.stock import (
	create_stock,
	get_stock,
	purchase_stock,
	cancel_purchase,
	delete_stock,
)


class StockCoreTests(TestCase):
	def setUp(self):
		self.usuario = Usuario.objects.create(
			nombre="Cliente 1",
			correo="cliente1@example.com",
			contraseña="secret",
			direccion="Calle 123",
			tipo="comprador",
		)
		self.producto = Producto.objects.create(
			nombre="Juguete A",
			precio=100,
			usuario=self.usuario,
			descripcion="Juguete de prueba",
			stock=0,
		)

	def test_create_and_read_stock(self):
		create_stock(self.producto.id, 20)
		self.producto.refresh_from_db()
		self.assertEqual(self.producto.stock, 20)
		self.assertEqual(get_stock(self.producto.id), 20)

	def test_purchase_updates_stock(self):
		create_stock(self.producto.id, 10)
		purchase_stock(self.producto.id, 3)
		self.producto.refresh_from_db()
		self.assertEqual(self.producto.stock, 7)

	def test_purchase_not_enough_stock_raises(self):
		create_stock(self.producto.id, 2)
		with self.assertRaises(ValueError):
			purchase_stock(self.producto.id, 5)

	def test_cancel_purchase_restores_stock(self):
		create_stock(self.producto.id, 5)
		purchase_stock(self.producto.id, 4)
		cancel_purchase(self.producto.id, 2)
		self.producto.refresh_from_db()
		self.assertEqual(self.producto.stock, 3)

	def test_delete_stock_sets_zero(self):
		create_stock(self.producto.id, 8)
		delete_stock(self.producto.id)
		self.producto.refresh_from_db()
		self.assertEqual(self.producto.stock, 0)


from django.db import transaction
from .models import Producto


def _get_product(product_id: int) -> Producto:
    try:
        return Producto.objects.get(id=product_id)
    except Producto.DoesNotExist as exc:
        raise ValueError("Producto no encontrado") from exc


def create_stock(product_id: int, cantidad: int) -> Producto:
    if cantidad < 0:
        raise ValueError("La cantidad inicial no puede ser negativa")
    producto = _get_product(product_id)
    producto.stock = cantidad
    producto.save(update_fields=["stock"])
    return producto


def get_stock(product_id: int) -> int:
    producto = _get_product(product_id)
    return producto.stock


@transaction.atomic
def purchase_stock(product_id: int, cantidad: int) -> Producto:
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser positiva")
    producto = _get_product(product_id)
    if producto.stock < cantidad:
        raise ValueError("Stock insuficiente")
    producto.stock -= cantidad
    producto.save(update_fields=["stock"])
    return producto


@transaction.atomic
def cancel_purchase(product_id: int, cantidad: int) -> Producto:
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser positiva")
    producto = _get_product(product_id)
    producto.stock += cantidad
    producto.save(update_fields=["stock"])
    return producto


def delete_stock(product_id: int) -> Producto:
    """
    Política: no borrar el producto ni su registro de stock; dejarlo en 0.
    """
    producto = _get_product(product_id)
    if producto.stock != 0:
        producto.stock = 0
        producto.save(update_fields=["stock"])
    return producto

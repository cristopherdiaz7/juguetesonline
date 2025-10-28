# 🧸 JuguetesOnline - E-commerce de Juguetes Coleccionables

**JuguetesOnline** es un sitio web de comercio electrónico para la compra y venta de juguetes coleccionables, desarrollado como proyecto académico utilizando **Django**

## 🔧 Tecnologías utilizadas

- **Django**: framework web principal (backend)
- **Visual Studio Code**: editor de código
- **HTML/CSS**: diseño y estructura del frontend
- **MySQL**: sistema de base de datos
- **Postman**: pruebas de APIs

El sistema incluye varios modelos

- **Usuario**: compradores y vendedores
- **Producto**: juguetes publicados por los vendedores
- **CarritoDeCompras**: carrito de cada usuario
- **CarritoProducto**: productos agregados al carrito
- **Pedido**: resumen de la compra
- **Pago**: información del pago del pedido
- **Envio**: datos de la entrega
- **Reseña**: calificaciones y comentarios de los usuarios

Funcionalidades principales
Registro de usuarios (compradores o vendedores)

Publicación de productos

Carrito de compras funcional

Gestión de pedidos, pagos y envíos

Reseñas y calificaciones de productos.

👨‍💻 Autor
Cristopher Leonel Díaz

Facultad: Universidad de Mendoza

Año: 2025

## ✅ TP4 – Pruebas y correcciones sobre la funcionalidad core de la API

Se implementaron pruebas automáticas para las funcionalidades principales del e-commerce, asegurando que la API funcione correctamente antes de ser usada por el frontend.

### 📦 Archivos de pruebas

#### 1. `ventas/tests.py` - Pruebas CRUD de Stock (5 tests)
Cobertura:
- ✅ Crear y leer stock inicial
- ✅ Descontar stock al comprar
- ✅ Error si se intenta comprar más del disponible
- ✅ Restaurar stock al cancelar compra
- ✅ Eliminar stock dejando el valor en 0

Lógica de stock (`ventas/stock.py`):
- `create_stock(product_id, cantidad)` - Crear registro de stock nuevo
- `get_stock(product_id)` - Consultar cantidad disponible
- `purchase_stock(product_id, cantidad)` - Actualizar stock al comprar (transaccional)
- `cancel_purchase(product_id, cantidad)` - Reponer stock al cancelar (transaccional)
- `delete_stock(product_id)` - Eliminar stock (deja en 0)

#### 2. `ventas/test_api_funcionalidades.py` - Pruebas de funcionalidades principales (7 tests)
Cobertura:
- ✅ **Test 1**: Registro de usuarios - Verifica que un nuevo usuario pueda registrarse mediante la API
- ✅ **Test 2**: Login de usuarios - Verifica autenticación con credenciales válidas
- ✅ **Test 3**: Agregado de productos - Verifica que un vendedor pueda registrar productos
- ✅ **Test 4**: Listado de productos - Verifica que el endpoint de listado funcione correctamente
- ✅ **Test 5**: Agregar producto al carrito - Verifica que un usuario pueda agregar productos a su carrito
- ✅ **Test 6**: Crear pedido desde carrito - Verifica generación correcta de pedidos
- ✅ **Test 7**: Flujo completo de compra - Test de integración end-to-end

### 🚀 Cómo ejecutar las pruebas

#### Método 1: Terminal (recomendado)

1. **Activar entorno virtual**
   ```powershell
   .\venv\Scripts\activate
   ```

2. **Ejecutar TODAS las pruebas de ventas (12 tests)**
   ```powershell
   python manage.py test ventas -v 2
   ```

3. **Ejecutar solo pruebas de Stock (5 tests)**
   ```powershell
   python manage.py test ventas.tests -v 2
   ```

4. **Ejecutar solo pruebas de Funcionalidades API (7 tests)**
   ```powershell
   python manage.py test ventas.test_api_funcionalidades -v 2
   ```

#### Método 2: Panel Testing de VS Code (opcional)

1. Asegurate de tener la extensión "Python" (Microsoft) habilitada
2. Abrí un archivo `.py` (por ejemplo `ventas/tests.py`)
3. Presioná `Ctrl+Shift+P` → "Python: Configure Tests" → elegí `unittest`
4. Carpeta: `ventas` → Patrón: `test*.py`
5. Recargá la ventana: `Ctrl+Shift+P` → "Developer: Reload Window"
6. En el panel Testing, tocá "Refresh". Deberían aparecer los 12 tests

**Troubleshooting:**
- Si aparece "Unittest Discovery Error": seleccioná el intérprete del venv (`Ctrl+Shift+P` → "Python: Select Interpreter")
- Ver Output → desplegable: "Python Test Log" para detalles del error
- Verificá que en `.vscode/settings.json` esté `unittest` activado y `pytest`/`nose` desactivados

### 📊 Resultados esperados

Todos los tests deben pasar:
```
Ran 12 tests in 0.078s
OK
```

- **5 tests de Stock** ✅
- **7 tests de Funcionalidades API** ✅

### 📝 Notas importantes

- **Base de datos de prueba**: Durante los tests se usa SQLite automáticamente (memoria), sin depender de permisos MySQL
- **Aislamiento**: Django crea una BD temporal solo para pruebas, por lo que no afecta tu BD de desarrollo
- **URLs de la API**: Los endpoints están bajo `/api/dualcash/model/` (corregido con slash final)
- **Transacciones**: Las funciones de compra/cancelación de stock usan `@transaction.atomic` para garantizar consistencia

### 🎯 Propósito del TP4

Estas pruebas automáticas:
- ✅ Simulan el uso real de la API como lo haría el frontend
- ✅ Aseguran que todo funcione correctamente antes de desplegar
- ✅ Evitan errores lógicos que podrían romper el sitio en producción
- ✅ Mantienen una base de datos limpia y controlada para testing

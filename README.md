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

## 🔐 TP5 – Autenticación JWT

Se implementó autenticación mediante JSON Web Tokens (JWT) reemplazando el sistema de sesiones y cookies de Django.

### 🎯 Cambios implementados

#### 1. Configuración JWT (settings.py)
- ✅ Instalado `djangorestframework-simplejwt`
- ✅ Cambiado de `SessionAuthentication` a `JWTAuthentication`
- ✅ Configurado tiempo de vida de tokens:
  - Access Token: 60 minutos
  - Refresh Token: 1 día

#### 2. Endpoints JWT
- 🔑 `POST /api/token/` - Obtener tokens (access y refresh)
- 🔄 `POST /api/token/refresh/` - Refrescar access token
- 📝 `POST /api/user/register/` - Registro de usuarios (público)

#### 3. Vistas protegidas
Todos los endpoints requieren autenticación JWT excepto:
- Registro de usuarios
- Obtener tokens
- Listar productos (solo lectura)

### 🚀 Cómo usar JWT con Postman

#### Paso 1: Registrar un usuario

**Endpoint:** `POST http://localhost:8000/api/user/register/`

**Body (JSON):**
```json
{
  "username": "usuario_test",
  "password": "mipassword123",
  "email": "test@example.com",
  "tipo": "comprador",
  "direccion": "Calle Test 123"
}
```

**Respuesta esperada:**
```json
{
  "message": "Usuario registrado correctamente",
  "user": {
    "id": 1,
    "username": "usuario_test",
    "email": "test@example.com",
    "tipo": "comprador"
  },
  "instrucciones": "Usa POST /api/token/ para obtener tu token JWT"
}
```

#### Paso 2: Obtener tokens JWT (Login)

**Endpoint:** `POST http://localhost:8000/api/token/`

**Body (JSON):**
```json
{
  "username": "usuario_test",
  "password": "mipassword123"
}
```

**Respuesta esperada:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

💡 **Guarda el `access` token**, lo necesitarás para los siguientes pasos.

#### Paso 3: Acceder a endpoints protegidos

**Ejemplo:** Listar usuarios

**Endpoint:** `GET http://localhost:8000/api/user/usuarios/`

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

En Postman:
1. Ve a la pestaña "Headers"
2. Agrega un header:
   - **Key:** `Authorization`
   - **Value:** `Bearer [tu_access_token_aquí]`

#### Paso 4: Refrescar el token

Cuando el access token expire (después de 60 minutos), usá el refresh token:

**Endpoint:** `POST http://localhost:8000/api/token/refresh/`

**Body (JSON):**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Respuesta:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  // Nuevo token
}
```

### 📋 Lista completa de endpoints

#### Públicos (sin autenticación)
- `POST /api/user/register/` - Registrar usuario
- `POST /api/token/` - Obtener tokens (login)
- `POST /api/token/refresh/` - Refrescar token
- `GET /api/dualcash/model/productos/` - Listar productos

#### Protegidos (requieren JWT)
- `GET /api/user/usuarios/` - Listar usuarios
- `GET /api/user/usuarios/{id}/` - Detalle de usuario
- `PUT /api/user/usuarios/{id}/` - Actualizar usuario
- `DELETE /api/user/usuarios/{id}/` - Eliminar usuario
- `POST /api/dualcash/model/productos/` - Crear producto
- `PUT /api/dualcash/model/productos/{id}/` - Actualizar producto
- `DELETE /api/dualcash/model/productos/{id}/` - Eliminar producto
- `GET /api/dualcash/model/carritos/` - Listar carritos
- `POST /api/dualcash/model/carritos/` - Crear carrito
- `GET /api/dualcash/model/pedidos/` - Listar pedidos
- `POST /api/dualcash/model/pedidos/` - Crear pedido

### 🛠️ Iniciar el servidor

```powershell
# Activar venv
.\venv\Scripts\activate

# Iniciar servidor
python manage.py runserver
```

### ❌ Cambios removidos del TP3

Con la implementación de JWT, los siguientes endpoints de sesiones **ya no están disponibles**:
- ❌ `POST /api/user/login/` (reemplazado por `/api/token/`)
- ❌ `POST /api/user/logout/` (no es necesario con JWT)

Para "cerrar sesión" con JWT simplemente eliminá el token del lado del cliente (navegador/app).

### 📝 Notas importantes

- **Sin cookies:** JWT se envía en headers, no en cookies
- **Stateless:** El servidor no mantiene sesiones, todo está en el token
- **CORS habilitado:** Configurado para permitir requests desde cualquier origen (desarrollo)
- **Tests:** Los tests del TP4 se actualizarán para usar JWT en lugar de sesiones


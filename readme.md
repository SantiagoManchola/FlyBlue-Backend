# FlyBlue Backend API


Sistema de gestión de vuelos desarrollado con FastAPI (modo asíncrono), PostgreSQL y autenticación JWT. Este proyecto está completamente automatizado con un flujo **CI/CD** usando **Azure DevOps**, desplegando en **Azure App Service para Contenedores**.

## 🚀 Características

- **Autenticación JWT** completa con roles de usuario (cliente y admin).
- **Gestión de vuelos** (búsqueda, reservas, pagos).
- **Panel de administración** para gestionar ciudades, vuelos y equipajes.
- **Base de datos PostgreSQL** (lista para usarse con Docker).
- **Documentación automática** (Swagger/OpenAPI) disponible en `/docs`.
- **CI/CD Automatizado** con Azure DevOps.
- **Despliegue multi-entorno** (Dev, Test, Prod).

## ☁️ Entornos Desplegados

El pipeline de CI/CD despliega automáticamente en los siguientes entornos basados en la rama de Git:

| Entorno | Rama de Git | URL Base de la API                                                                                     |
| :--- | :--- |:-------------------------------------------------------------------------------------------------------|
| **Desarrollo** | `develop` | `flyblue-api-server-dev-g0a8bsfaethdehe0.canadacentral-01.azurewebsites.net`                           |
| **Pruebas** | `test` | `flyblue-api-server-test-gaheeyd2e7hybwau.canadacentral-01.azurewebsites.net`                                                                                                     |
| **Producción** | `main` | `flyblue-api-server-main-hzdma8gyhudag8bq.canadacentral-01.azurewebsites.net`                          |

## 📋 Requisitos

- Docker y Docker Compose (para desarrollo local)
- Python 3.11+ (para desarrollo local sin Docker)
- PostgreSQL (incluido en Docker)


## ⚙️ Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/SantiagoManchola/FlyBlue-Backend.git
cd FlyBlue-Backend
```

### 2. Configurar variables de entorno (archivo .env)
```bash
# Ajustar archivo .env (quitarle el .example y cambiar valores)
cp .env.example .env

# Editar .env con tus valores (opcional, los valores por defecto funcionan)
```

### 3. Ejecutar con Docker
```bash
# Construir y ejecutar contenedores
docker-compose up --build

# En segundo plano
docker-compose up -d --build
```

### 4. Verificar instalación
- **API:** http://localhost:8000
- **Documentación:** http://localhost:8000/docs
- **Base de datos:** localhost:5432

## 🔐 Autenticación

### Registro de usuario
```http
POST /v1/auth/register
Content-Type: application/json

{
    "nombre": "Juan Pérez",
    "correo": "juan@example.com",
    "contraseña": "123456"
}
```

### Iniciar sesión
```http
POST /v1/auth/login
Content-Type: application/json

{
    "correo": "juan@example.com",
    "contraseña": "123456"
}
```

**Respuesta:**
```json
{
    "id_usuario": 1,
    "nombre": "Juan Pérez",
    "correo": "juan@example.com",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Usar el token
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## 📚 Endpoints de la API

### 🔓 Endpoints Públicos (sin autenticación)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/v1/auth/register` | Registrar nuevo usuario |
| POST | `/v1/auth/login` | Iniciar sesión |

### 🔒 Endpoints Protegidos (requieren token)

#### Perfil de Usuario
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/v1/auth/me` | Obtener perfil del usuario autenticado |

#### Consultas Generales
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/v1/vuelos` | Buscar vuelos por origen, destino y fecha |
| GET | `/v1/vuelos/{id}` | Obtener detalles de un vuelo |
| GET | `/v1/vuelos/{id_vuelo}/asientos` | Obtener asientos de un vuelo |
| GET | `/v1/ciudades` | Listar todas las ciudades |
| GET | `/v1/equipajes` | Listar tipos de equipaje |

#### Gestión de Reservas (Cliente)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/v1/cliente/reservas` | Crear nueva reserva |
| GET | `/v1/cliente/reservas/{id_usuario}` | Obtener reservas de un usuario |
| POST | `/v1/cliente/reservas/{id}/pago` | Procesar pago de reserva |

#### Administración (Solo Admin)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/v1/admin/ciudades` | Crear nueva ciudad |
| POST | `/v1/admin/equipajes` | Crear tipo de equipaje |
| POST | `/v1/admin/vuelos` | Crear nuevo vuelo |

## 📖 Ejemplos de Uso

### Buscar vuelos
```http
GET /v1/vuelos?origen=1&destino=2&fecha=2025-11-15
Authorization: Bearer {token}
```

### Crear reserva
```http
POST /v1/cliente/reservas
Authorization: Bearer {token}
Content-Type: application/json

{
    "id_usuario": 1,
    "id_vuelo": 1,
    "id_asiento": 5,
    "id_equipaje": 2
}
```

### Crear ciudad (Admin)
```http
POST /v1/admin/ciudades
Authorization: Bearer {token}
Content-Type: application/json

{
    "nombre": "Bogotá",
    "codigo": "BOG"
}
```

### Crear vuelo (Admin)
```http
POST /v1/admin/vuelos
Authorization: Bearer {token}
Content-Type: application/json

{
    "id_origen": 1,
    "id_destino": 2,
    "fecha_salida": "2025-11-15T08:00:00",
    "fecha_llegada": "2025-11-15T10:00:00",
    "precio_base": 250.00
}
```

## 🗄️ Base de Datos

### Estructura de Tablas

- **usuario**: Usuarios del sistema (clientes y administradores)
- **ciudad**: Ciudades disponibles para vuelos
- **vuelo**: Información de vuelos
- **asiento**: Asientos por vuelo
- **equipaje**: Tipos de equipaje disponibles
- **reserva**: Reservas de vuelos
- **pago**: Pagos de reservas


## 🔧 Desarrollo

### Ejecutar sin Docker
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos local en .env
DATABASE_URL=postgresql://user:password@localhost:5432/flyblue

# Ejecutar aplicación
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Comandos útiles de Docker
```bash
# Ver logs
docker-compose logs -f

# Parar contenedores
docker-compose down

# Reconstruir solo la API
docker-compose up --build web

# Acceder al contenedor
docker exec -it api_app bash

# Acceder a PostgreSQL
docker exec -it postgres_db psql -U myuser -d mydb
```

## 🔒 Seguridad

- **Autenticación JWT** sin expiración
- **Autorización por roles** (usuario/admin)
- **Validación de permisos** en cada endpoint
- **Encriptación de contraseñas** con bcrypt
- **Validación de datos** con Pydantic


## 🚨 Códigos de Error

| Código | Descripción |
|--------|-------------|
| 400 | Solicitud incorrecta |
| 401 | Token inválido o faltante |
| 403 | Sin permisos suficientes |
| 404 | Recurso no encontrado |
| 500 | Error interno del servidor |

## 📊 Roles de Usuario

### Usuario (cliente)
- Buscar vuelos
- Ver detalles de vuelos y asientos
- Crear reservas propias
- Ver sus reservas
- Procesar pagos

### Administrador
- Todas las funciones de usuario
- Crear ciudades
- Crear tipos de equipaje
- Crear vuelos
- Ver reservas de cualquier usuario

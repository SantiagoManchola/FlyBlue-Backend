Revisar lo de asientos disponibles y totales en la base de datos

**.env ejemplo**
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=mydb
POSTGRES_HOST=db
POSTGRES_PORT=5432

DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

**cambios en la estructura inicial de bd**
- Asientos totales se elimino la condicion de NOT NULL (falta definir si es mejor de manera dinamica cada que se cree un asiento relacionado a un vuelo y cada vez que se reserve un vuelo se acrualicen en la base de datos, o hacerlo al llamado de asientos unicamente)
- En la tabla de equipaje se elimino la resticcion de check varchar (grande,pequeño,mediano), para que el admin puedieraa crear diferentes equipajes
- 


**Creacion de las tablas de la base de datos**
-- 1️⃣ Tabla: Usuario
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    rol VARCHAR(20) CHECK (rol IN ('usuario', 'admin')) NOT NULL
);

-- 2️⃣ Tabla: Ciudad
CREATE TABLE IF NOT EXISTS ciudad (
    id_ciudad SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo VARCHAR(10) NOT NULL
);

-- 3️⃣ Tabla: Vuelo
CREATE TABLE IF NOT EXISTS vuelo (
    id_vuelo SERIAL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL,
    id_origen INT NOT NULL REFERENCES ciudad(id_ciudad) ON DELETE CASCADE,
    id_destino INT NOT NULL REFERENCES ciudad(id_ciudad) ON DELETE CASCADE,
    fecha_salida TIMESTAMP NOT NULL,
    fecha_llegada TIMESTAMP NOT NULL,
    precio_base DECIMAL(10, 2) NOT NULL,
    asientos_totales INT,
    asientos_disponibles INT
);

-- 4️⃣ Tabla: Asiento
CREATE TABLE IF NOT EXISTS asiento (
    id_asiento SERIAL PRIMARY KEY,
    id_vuelo INT NOT NULL REFERENCES vuelo(id_vuelo) ON DELETE CASCADE,
    fila INT NOT NULL,
    columna VARCHAR(1) CHECK (columna IN ('A', 'B', 'C', 'D', 'E')) NOT NULL,
    disponible BOOLEAN DEFAULT TRUE
);

-- 5️⃣ Tabla: Equipaje
CREATE TABLE IF NOT EXISTS equipaje (
    id_equipaje SERIAL PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    descripcion VARCHAR(20) NOT NULL,
    peso_maximo INT not null
);



-- 6️⃣ Tabla: Reserva
CREATE TABLE IF NOT EXISTS reserva (
    id_reserva SERIAL PRIMARY KEY,
    id_usuario INT NOT NULL REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    id_vuelo INT NOT NULL REFERENCES vuelo(id_vuelo) ON DELETE CASCADE,
    id_asiento INT NOT NULL REFERENCES asiento(id_asiento) ON DELETE SET NULL,
    id_equipaje INT REFERENCES equipaje(id_equipaje),
    total DECIMAL(10, 2) NOT NULL
);

-- 7️⃣ Tabla: Pago
CREATE TABLE IF NOT EXISTS pago (
    id_pago SERIAL PRIMARY KEY,
    id_reserva INT NOT NULL REFERENCES reserva(id_reserva) ON DELETE CASCADE,
    monto DECIMAL(10, 2) NOT NULL,
    estado VARCHAR(20) CHECK (estado IN ('pagado', 'fallido')) NOT NULL,
    fecha TIMESTAMP DEFAULT NOW()
);

**Crear datos de prueba**
en el txt estan datos de prueba o pueden crear diferentes, se inyectaron con sql directo en la base de datos

**Para probar la app tener en cuenta**
Aun falta el JWT que nos retorna el token, por lo que las consultas de admin y de cliente necesitan estar linkeadas al usuario por ahora se le va a pasar el id_usuario, ya luego no sera necesario
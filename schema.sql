-- ============================================================
-- CineGest - Script SQL para PostgreSQL
-- ============================================================

-- Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'cliente' CHECK (rol IN ('admin', 'cliente')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Películas
CREATE TABLE IF NOT EXISTS peliculas (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    duracion INTEGER NOT NULL,  -- en minutos
    genero VARCHAR(50),
    clasificacion VARCHAR(10),
    imagen_url TEXT,
    trailer_url TEXT,
    estado VARCHAR(20) NOT NULL DEFAULT 'activa' CHECK (estado IN ('activa', 'inactiva')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Funciones (proyecciones)
CREATE TABLE IF NOT EXISTS funciones (
    id SERIAL PRIMARY KEY,
    pelicula_id INTEGER NOT NULL REFERENCES peliculas(id) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    sala VARCHAR(50) NOT NULL DEFAULT 'Sala 1',
    precio NUMERIC(10,2) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'disponible' CHECK (estado IN ('disponible', 'cancelada')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Evitar traslapes: no puede haber dos funciones en la misma sala, misma fecha y misma hora
    UNIQUE (sala, fecha, hora)
);

-- Asientos (estructura fija de la sala)
CREATE TABLE IF NOT EXISTS asientos (
    id SERIAL PRIMARY KEY,
    numero INTEGER NOT NULL,
    fila CHAR(1) NOT NULL,
    columna INTEGER NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    UNIQUE (fila, columna)
);

-- Tiquetes
CREATE TABLE IF NOT EXISTS tiquetes (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    funcion_id INTEGER NOT NULL REFERENCES funciones(id) ON DELETE RESTRICT,
    fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total NUMERIC(10,2) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo' CHECK (estado IN ('activo', 'usado', 'cancelado'))
);

-- Detalle de tiquetes (relación muchos-a-muchos entre tiquete y asientos)
CREATE TABLE IF NOT EXISTS detalle_tiquete (
    id SERIAL PRIMARY KEY,
    tiquete_id INTEGER NOT NULL REFERENCES tiquetes(id) ON DELETE CASCADE,
    asiento_id INTEGER NOT NULL REFERENCES asientos(id) ON DELETE RESTRICT,
    precio_unitario NUMERIC(10,2) NOT NULL,
    -- RESTRICCIÓN CRÍTICA: un asiento no puede venderse dos veces para la misma función
    UNIQUE (tiquete_id, asiento_id)
);

-- Tabla auxiliar para controlar asientos ocupados por función
CREATE TABLE IF NOT EXISTS funcion_asientos (
    id SERIAL PRIMARY KEY,
    funcion_id INTEGER NOT NULL REFERENCES funciones(id) ON DELETE CASCADE,
    asiento_id INTEGER NOT NULL REFERENCES asientos(id) ON DELETE CASCADE,
    tiquete_id INTEGER NOT NULL REFERENCES tiquetes(id) ON DELETE CASCADE,
    UNIQUE (funcion_id, asiento_id)  -- REGLA CRÍTICA: asiento único por función
);

-- ============================================================
-- Datos iniciales: Admin por defecto
-- Contraseña: admin123 (hash generado con werkzeug)
-- ============================================================
INSERT INTO usuarios (nombre, email, contrasena, rol)
VALUES ('Administrador', 'admin@cinegest.com', 'scrypt:32768:8:1$placeholder$hash', 'admin')
ON CONFLICT (email) DO NOTHING;

-- ============================================================
-- Precargar 150 asientos: 10 filas (A-J) x 15 columnas
-- ============================================================
DO $$
DECLARE
    filas CHAR[] := ARRAY['A','B','C','D','E','F','G','H','I','J'];
    f CHAR;
    c INTEGER;
    num INTEGER := 1;
BEGIN
    FOREACH f IN ARRAY filas LOOP
        FOR c IN 1..15 LOOP
            INSERT INTO asientos (numero, fila, columna)
            VALUES (num, f, c)
            ON CONFLICT (fila, columna) DO NOTHING;
            num := num + 1;
        END LOOP;
    END LOOP;
END $$;

-- ============================================================
-- Índices para mejorar rendimiento
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_funciones_pelicula ON funciones(pelicula_id);
CREATE INDEX IF NOT EXISTS idx_tiquetes_funcion ON tiquetes(funcion_id);
CREATE INDEX IF NOT EXISTS idx_funcion_asientos_funcion ON funcion_asientos(funcion_id);
CREATE INDEX IF NOT EXISTS idx_tiquetes_codigo ON tiquetes(codigo);

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

-- =========================
-- Películas iniciales
-- =========================
INSERT INTO peliculas (titulo, descripcion, duracion, genero, clasificacion, imagen_url) VALUES
('The Matrix', 'Un hacker descubre la realidad', 136, 'Ciencia Ficcion', 'PG-13', 'https://image.tmdb.org/t/p/w500/aOIuZAjPaRIE6CMzbazvcHuHXDc.jpg'),
('Gladiator', 'Un general romano busca venganza', 155, 'Accion', 'R', 'https://image.tmdb.org/t/p/w500/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg'),
('Avengers: Endgame', 'Batalla final contra Thanos', 181, 'Accion', 'PG-13', 'https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg'),
('Joker', 'Origen del villano de Gotham', 122, 'Drama', 'R', 'https://image.tmdb.org/t/p/w500/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg'),
('Spider-Man: No Way Home', 'Multiverso arácnido', 148, 'Accion', 'PG-13', 'https://image.tmdb.org/t/p/w500/1g0dhYtq4irTY1GPXvft6k4YLjm.jpg'),
('The Lion King', 'Historia del rey leon', 88, 'Animacion', 'G', 'https://image.tmdb.org/t/p/w500/2bXbqYdUdNVa8VIWXVfclP2ICtT.jpg'),
('Frozen', 'Reino de hielo', 102, 'Animacion', 'PG', 'https://image.tmdb.org/t/p/w500/kgwjIb2JDHRhNk13lmSxiClFjVk.jpg'),
('Black Panther', 'Wakanda protege su legado', 134, 'Accion', 'PG-13', 'https://image.tmdb.org/t/p/w500/uxzzxijgPIY7slzFvMotPv8wjKA.jpg'),
('Doctor Strange', 'Magia y multiverso', 115, 'Accion', 'PG-13', 'https://image.tmdb.org/t/p/w500/uGBVj3bEbCoZbDjjl9wTxcygko1.jpg'),
('Harry Potter', 'Inicio en Hogwarts', 152, 'Fantasia', 'PG', 'https://image.tmdb.org/t/p/w500/wuMc08IPKEatf9rnMNXvIDxqP4W.jpg'),
('Lord of the Rings', 'La comunidad del anillo', 178, 'Fantasia', 'PG-13', 'https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg'),
('Star Wars', 'Una nueva esperanza', 121, 'Ciencia Ficcion', 'PG', 'https://image.tmdb.org/t/p/w500/6FfCtAuVAW8XJjZ7eWeLibRLWTw.jpg'),
('Deadpool', 'Antihéroe irreverente', 108, 'Accion', 'R', 'https://image.tmdb.org/t/p/w500/3E53WEZJqP6aM84D8CckXx4pIHw.jpg'),
('Venom', 'Simbionte alienigena', 112, 'Accion', 'PG-13', 'https://image.tmdb.org/t/p/w500/2uNW4WbgBXL25BAbXGLnLqX71Sw.jpg');

-- =========================
-- Funciones iniciales
-- =========================
INSERT INTO funciones (pelicula_id, fecha, hora, sala, precio) VALUES
(1, CURRENT_DATE, '10:00', 'Sala 1', 12000),
(2, CURRENT_DATE, '11:30', 'Sala 1', 12000),
(3, CURRENT_DATE, '13:00', 'Sala 1', 12000),
(4, CURRENT_DATE, '14:30', 'Sala 1', 12000),
(5, CURRENT_DATE, '16:00', 'Sala 1', 12000),
(6, CURRENT_DATE, '17:30', 'Sala 2', 12000),
(7, CURRENT_DATE, '19:00', 'Sala 2', 12000),
(8, CURRENT_DATE, '20:30', 'Sala 2', 12000),
(9, CURRENT_DATE, '22:00', 'Sala 2', 12000),
(10, CURRENT_DATE, '12:00', 'Sala 3', 12000),
(11, CURRENT_DATE, '15:00', 'Sala 3', 12000),
(12, CURRENT_DATE, '18:00', 'Sala 3', 12000),
(13, CURRENT_DATE, '21:00', 'Sala 3', 12000),
(14, CURRENT_DATE, '23:00', 'Sala 3', 12000);
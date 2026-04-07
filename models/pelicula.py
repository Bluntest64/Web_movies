from database import query


class Pelicula:
    @staticmethod
    def listar(solo_activas=False):
        if solo_activas:
            return query("SELECT * FROM peliculas WHERE estado='activa' ORDER BY titulo", fetchall=True)
        return query("SELECT * FROM peliculas ORDER BY titulo", fetchall=True)

    @staticmethod
    def buscar_por_id(pid):
        return query("SELECT * FROM peliculas WHERE id=%s", (pid,), fetchone=True)

    @staticmethod
    def crear(titulo, descripcion, duracion, genero, clasificacion, imagen_url, trailer_url, estado='activa'):
        return query(
            """INSERT INTO peliculas (titulo, descripcion, duracion, genero, clasificacion, imagen_url, trailer_url, estado)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
            (titulo, descripcion, duracion, genero, clasificacion, imagen_url, trailer_url, estado),
            fetchone=True, commit=True
        )

    @staticmethod
    def actualizar(pid, titulo, descripcion, duracion, genero, clasificacion, imagen_url, trailer_url, estado):
        query(
            """UPDATE peliculas SET titulo=%s, descripcion=%s, duracion=%s, genero=%s,
               clasificacion=%s, imagen_url=%s, trailer_url=%s, estado=%s WHERE id=%s""",
            (titulo, descripcion, duracion, genero, clasificacion, imagen_url, trailer_url, estado, pid),
            commit=True
        )

    @staticmethod
    def eliminar(pid):
        query("DELETE FROM peliculas WHERE id=%s", (pid,), commit=True)

    @staticmethod
    def mas_vistas(limite=5):
        return query("""
            SELECT p.titulo, COUNT(t.id) as total_ventas
            FROM peliculas p
            JOIN funciones f ON f.pelicula_id = p.id
            JOIN tiquetes t ON t.funcion_id = f.id
            WHERE t.estado != 'cancelado'
            GROUP BY p.id, p.titulo
            ORDER BY total_ventas DESC
            LIMIT %s
        """, (limite,), fetchall=True)

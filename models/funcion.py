from database import query


class Funcion:
    @staticmethod
    def listar(pelicula_id=None, solo_disponibles=False):
        conditions = []
        params = []
        if pelicula_id:
            conditions.append("f.pelicula_id = %s")
            params.append(pelicula_id)
        if solo_disponibles:
            conditions.append("f.estado = 'disponible'")
            conditions.append("f.fecha >= CURRENT_DATE")
        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        sql = f"""
            SELECT f.*, p.titulo as pelicula_titulo, p.duracion as pelicula_duracion,
                   p.imagen_url, p.clasificacion, p.genero,
                   (SELECT COUNT(*) FROM funcion_asientos fa WHERE fa.funcion_id = f.id) as asientos_ocupados
            FROM funciones f
            JOIN peliculas p ON p.id = f.pelicula_id
            {where}
            ORDER BY f.fecha, f.hora
        """
        return query(sql, params if params else None, fetchall=True)

    @staticmethod
    def buscar_por_id(fid):
        return query("""
            SELECT f.*, p.titulo as pelicula_titulo, p.duracion as pelicula_duracion,
                   p.imagen_url, p.clasificacion, p.descripcion as pelicula_descripcion
            FROM funciones f
            JOIN peliculas p ON p.id = f.pelicula_id
            WHERE f.id = %s
        """, (fid,), fetchone=True)

    @staticmethod
    def crear(pelicula_id, fecha, hora, sala, precio, estado='disponible'):
        # Verificar traslape: misma sala, misma fecha y hora
        traslape = query(
            "SELECT id FROM funciones WHERE sala=%s AND fecha=%s AND hora=%s",
            (sala, fecha, hora), fetchone=True
        )
        if traslape:
            raise ValueError("Ya existe una función programada en esa sala, fecha y hora.")
        return query(
            "INSERT INTO funciones (pelicula_id, fecha, hora, sala, precio, estado) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
            (pelicula_id, fecha, hora, sala, precio, estado),
            fetchone=True, commit=True
        )

    @staticmethod
    def actualizar(fid, pelicula_id, fecha, hora, sala, precio, estado):
        traslape = query(
            "SELECT id FROM funciones WHERE sala=%s AND fecha=%s AND hora=%s AND id != %s",
            (sala, fecha, hora, fid), fetchone=True
        )
        if traslape:
            raise ValueError("Ya existe una función programada en esa sala, fecha y hora.")
        query(
            "UPDATE funciones SET pelicula_id=%s, fecha=%s, hora=%s, sala=%s, precio=%s, estado=%s WHERE id=%s",
            (pelicula_id, fecha, hora, sala, precio, estado, fid), commit=True
        )

    @staticmethod
    def eliminar(fid):
        query("DELETE FROM funciones WHERE id=%s", (fid,), commit=True)

    @staticmethod
    def asientos_ocupados(funcion_id):
        rows = query(
            "SELECT asiento_id FROM funcion_asientos WHERE funcion_id=%s",
            (funcion_id,), fetchall=True
        )
        return [r['asiento_id'] for r in rows] if rows else []

    @staticmethod
    def ocupacion(funcion_id):
        ocupados = query(
            "SELECT COUNT(*) as cnt FROM funcion_asientos WHERE funcion_id=%s",
            (funcion_id,), fetchone=True
        )
        return ocupados['cnt'] if ocupados else 0

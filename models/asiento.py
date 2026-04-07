from database import query


class Asiento:
    @staticmethod
    def listar_todos():
        return query("SELECT * FROM asientos WHERE estado='activo' ORDER BY fila, columna", fetchall=True)

    @staticmethod
    def listar_con_estado_funcion(funcion_id):
        """Retorna todos los asientos activos con su estado para una función específica"""
        return query("""
            SELECT a.*,
                   CASE WHEN fa.asiento_id IS NOT NULL THEN 'ocupado' ELSE 'disponible' END as estado_funcion
            FROM asientos a
            LEFT JOIN funcion_asientos fa ON fa.asiento_id = a.id AND fa.funcion_id = %s
            WHERE a.estado = 'activo'
            ORDER BY a.fila, a.columna
        """, (funcion_id,), fetchall=True)

    @staticmethod
    def buscar_por_id(aid):
        return query("SELECT * FROM asientos WHERE id=%s", (aid,), fetchone=True)

    @staticmethod
    def buscar_por_ids(ids):
        if not ids:
            return []
        placeholders = ','.join(['%s'] * len(ids))
        return query(f"SELECT * FROM asientos WHERE id IN ({placeholders})", tuple(ids), fetchall=True)

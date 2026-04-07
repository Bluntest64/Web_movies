import uuid
import psycopg2
from database import get_connection, query


class Tiquete:
    @staticmethod
    def generar_codigo():
        return str(uuid.uuid4()).replace('-', '').upper()[:12]

    @staticmethod
    def comprar(funcion_id, asiento_ids, usuario_id, precio_unitario):
        """Compra transaccional: crea tiquete + detalle + bloquea asientos en funcion_asientos"""
        codigo = Tiquete.generar_codigo()
        total = precio_unitario * len(asiento_ids)

        conn = get_connection()
        try:
            cur = conn.cursor()

            # Verificar que ningún asiento esté ya ocupado (con bloqueo)
            placeholders = ','.join(['%s'] * len(asiento_ids))
            cur.execute(
                f"SELECT asiento_id FROM funcion_asientos WHERE funcion_id=%s AND asiento_id IN ({placeholders}) FOR UPDATE",
                [funcion_id] + list(asiento_ids)
            )
            ocupados = cur.fetchall()
            if ocupados:
                raise ValueError("Uno o más asientos ya fueron vendidos. Por favor recarga la página.")

            # Insertar tiquete
            cur.execute(
                "INSERT INTO tiquetes (codigo, usuario_id, funcion_id, total, estado) VALUES (%s,%s,%s,%s,'activo') RETURNING id",
                (codigo, usuario_id, funcion_id, total)
            )
            tiquete_id = cur.fetchone()[0]

            # Insertar detalles y bloquear asientos
            for asiento_id in asiento_ids:
                cur.execute(
                    "INSERT INTO detalle_tiquete (tiquete_id, asiento_id, precio_unitario) VALUES (%s,%s,%s)",
                    (tiquete_id, asiento_id, precio_unitario)
                )
                cur.execute(
                    "INSERT INTO funcion_asientos (funcion_id, asiento_id, tiquete_id) VALUES (%s,%s,%s)",
                    (funcion_id, asiento_id, tiquete_id)
                )

            conn.commit()
            return {'id': tiquete_id, 'codigo': codigo, 'total': total}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def buscar_por_codigo(codigo):
        return query("""
            SELECT t.*, f.fecha, f.hora, f.sala, p.titulo as pelicula_titulo,
                   u.nombre as usuario_nombre
            FROM tiquetes t
            JOIN funciones f ON f.id = t.funcion_id
            JOIN peliculas p ON p.id = f.pelicula_id
            LEFT JOIN usuarios u ON u.id = t.usuario_id
            WHERE t.codigo = %s
        """, (codigo,), fetchone=True)

    @staticmethod
    def buscar_por_id(tid):
        return query("""
            SELECT t.*, f.fecha, f.hora, f.sala, p.titulo as pelicula_titulo,
                   u.nombre as usuario_nombre
            FROM tiquetes t
            JOIN funciones f ON f.id = t.funcion_id
            JOIN peliculas p ON p.id = f.pelicula_id
            LEFT JOIN usuarios u ON u.id = t.usuario_id
            WHERE t.id = %s
        """, (tid,), fetchone=True)

    @staticmethod
    def detalle_asientos(tiquete_id):
        return query("""
            SELECT a.fila, a.columna, a.numero, dt.precio_unitario
            FROM detalle_tiquete dt
            JOIN asientos a ON a.id = dt.asiento_id
            WHERE dt.tiquete_id = %s
            ORDER BY a.fila, a.columna
        """, (tiquete_id,), fetchall=True)

    @staticmethod
    def validar(codigo):
        tiquete = Tiquete.buscar_por_codigo(codigo)
        if not tiquete:
            return None, 'invalido'
        if tiquete['estado'] == 'usado':
            return tiquete, 'usado'
        if tiquete['estado'] == 'cancelado':
            return tiquete, 'cancelado'
        # Marcar como usado
        query("UPDATE tiquetes SET estado='usado' WHERE codigo=%s", (codigo,), commit=True)
        return tiquete, 'valido'

    @staticmethod
    def listar_por_usuario(usuario_id):
        return query("""
            SELECT t.*, p.titulo as pelicula_titulo, f.fecha, f.hora, f.sala
            FROM tiquetes t
            JOIN funciones f ON f.id = t.funcion_id
            JOIN peliculas p ON p.id = f.pelicula_id
            WHERE t.usuario_id = %s
            ORDER BY t.fecha_compra DESC
        """, (usuario_id,), fetchall=True)

    @staticmethod
    def total_ventas():
        result = query(
            "SELECT COALESCE(SUM(total),0) as total FROM tiquetes WHERE estado != 'cancelado'",
            fetchone=True
        )
        return result['total'] if result else 0

    @staticmethod
    def ventas_por_dia(dias=7):
        return query("""
            SELECT DATE(fecha_compra) as dia, COUNT(*) as cantidad, SUM(total) as ingresos
            FROM tiquetes
            WHERE estado != 'cancelado' AND fecha_compra >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY DATE(fecha_compra)
            ORDER BY dia DESC
        """, (dias,), fetchall=True)

    @staticmethod
    def listar_todos():
        return query("""
            SELECT t.*, p.titulo as pelicula_titulo, f.fecha, f.hora,
                   u.nombre as usuario_nombre
            FROM tiquetes t
            JOIN funciones f ON f.id = t.funcion_id
            JOIN peliculas p ON p.id = f.pelicula_id
            LEFT JOIN usuarios u ON u.id = t.usuario_id
            ORDER BY t.fecha_compra DESC
            LIMIT 100
        """, fetchall=True)

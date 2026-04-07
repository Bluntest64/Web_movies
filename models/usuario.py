from database import query
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario:
    @staticmethod
    def crear(nombre, email, contrasena, rol='cliente'):
        hash_pw = generate_password_hash(contrasena)
        return query(
            "INSERT INTO usuarios (nombre, email, contrasena, rol) VALUES (%s,%s,%s,%s) RETURNING id",
            (nombre, email, hash_pw, rol), fetchone=True, commit=True
        )

    @staticmethod
    def buscar_por_email(email):
        return query("SELECT * FROM usuarios WHERE email=%s", (email,), fetchone=True)

    @staticmethod
    def buscar_por_id(uid):
        return query("SELECT * FROM usuarios WHERE id=%s", (uid,), fetchone=True)

    @staticmethod
    def verificar_contrasena(email, contrasena):
        user = Usuario.buscar_por_email(email)
        if user and check_password_hash(user['contrasena'], contrasena):
            return user
        return None

    @staticmethod
    def listar():
        return query("SELECT id, nombre, email, rol, fecha_creacion FROM usuarios ORDER BY id", fetchall=True)

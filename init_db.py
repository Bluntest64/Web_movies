"""
Script de inicialización de la base de datos.
Ejecutar UNA VEZ después de aplicar schema.sql:
    python init_db.py
"""
import os
from dotenv import load_dotenv
load_dotenv()

import psycopg2
from werkzeug.security import generate_password_hash
from config import Config

def init():
    conn = psycopg2.connect(Config.DATABASE_URL)
    cur = conn.cursor()

    # Leer y ejecutar schema
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        sql = f.read()

    # Ejecutar el schema por bloques seguros
    cur.execute(sql)

    # Insertar / actualizar admin con contraseña real hasheada
    admin_pass = generate_password_hash('admin123')
    cur.execute("""
        INSERT INTO usuarios (nombre, email, contrasena, rol)
        VALUES (%s, %s, %s, 'admin')
        ON CONFLICT (email) DO UPDATE SET contrasena = EXCLUDED.contrasena
    """, ('Administrador', 'admin@cinegest.com', admin_pass))

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Base de datos inicializada correctamente.")
    print("   Admin: admin@cinegest.com / admin123")

if __name__ == '__main__':
    init()

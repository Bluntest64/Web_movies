import psycopg2
import psycopg2.extras
from config import Config


def get_connection():
    return psycopg2.connect(Config.DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)


def query(sql, params=None, fetchone=False, fetchall=False, commit=False):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        result = None
        if fetchone:
            result = cur.fetchone()
        elif fetchall:
            result = cur.fetchall()
        if commit:
            conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def execute_transaction(queries_params):
    """Execute multiple queries in a single transaction. queries_params = [(sql, params), ...]"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        results = []
        for sql, params in queries_params:
            cur.execute(sql, params or ())
            try:
                results.append(cur.fetchall())
            except Exception:
                results.append(None)
        conn.commit()
        return results
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

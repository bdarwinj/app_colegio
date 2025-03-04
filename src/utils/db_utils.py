# src/utils/db_utils.py
import sqlite3
from contextlib import contextmanager

@contextmanager
def db_cursor(db):
    """
    Context manager que obtiene un cursor de la conexión a la base de datos.
    Realiza commit si la operación se completa sin errores; en caso de excepción, ejecuta rollback.
    Al finalizar, cierra el cursor.
    """
    # Si el objeto db tiene el atributo 'connection', lo usamos; de lo contrario, asumimos que db es una conexión.
    connection = db.connection if hasattr(db, "connection") else db
    cursor = connection.cursor()
    try:
        yield cursor
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()

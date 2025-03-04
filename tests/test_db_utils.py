# tests/test_db_utils.py
import sqlite3
import unittest
from src.utils.db_utils import db_cursor

class TestDBUtils(unittest.TestCase):
    def setUp(self):
        # Crear una base de datos en memoria para las pruebas
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY AUTOINCREMENT, value TEXT)")
    
    def tearDown(self):
        self.conn.close()

    def test_commit(self):
        # Verificar que se confirme la transacción
        with db_cursor(self.conn) as cursor:
            cursor.execute("INSERT INTO test (value) VALUES (?)", ("hello",))
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM test")
        row = cur.fetchone()
        self.assertEqual(row["value"], "hello")

    def test_rollback(self):
        # Verificar que se realice rollback en caso de error
        try:
            with db_cursor(self.conn) as cursor:
                cursor.execute("INSERT INTO test (value) VALUES (?)", ("world",))
                raise Exception("Forced error")
        except Exception:
            pass
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM test")
        row = cur.fetchone()
        self.assertIsNone(row)

if __name__ == '__main__':
    unittest.main()

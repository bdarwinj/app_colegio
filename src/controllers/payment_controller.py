import sqlite3
import traceback
from datetime import datetime

class PaymentController:
    def __init__(self, db):
        """
        Initialize the PaymentController with a database object.
        'db' is expected to be a sqlite3.Connection or a custom Database object exposing a connection attribute.
        This initialization ensures that the 'payments' table exists.
        """
        self.db = db
        self.initialize_payments_table()

    def initialize_payments_table(self):
        """
        Create the 'payments' table if it does not exist.
        """
        try:
            if hasattr(self.db, "cursor") and callable(self.db.cursor):
                cursor = self.db.cursor()
            elif hasattr(self.db, "connection") and hasattr(self.db.connection, "cursor") and callable(self.db.connection.cursor):
                cursor = self.db.connection.cursor()
            else:
                raise AttributeError("El objeto de base de datos no proporciona un cursor válido mediante 'cursor()' o 'connection.cursor()'.")
            
            create_table_query = """
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    amount REAL,
                    description TEXT,
                    payment_date TEXT
                )
            """
            cursor.execute(create_table_query)
            if hasattr(self.db, "commit") and callable(self.db.commit):
                self.db.commit()
            elif hasattr(self.db, "connection") and hasattr(self.db.connection, "commit") and callable(self.db.connection.commit):
                self.db.connection.commit()
        except Exception as e:
            detailed_error = traceback.format_exc()
            print("Error al inicializar la tabla 'payments':")
            print(detailed_error)

    def register_payment(self, student_id, amount, description):
        """
        Inserts a new payment record into the payments table.
        Returns a tuple: (success, message, receipt_number, payment_date)
        In case of errors, the full traceback will be printed to the console.
        """
        try:
            if hasattr(self.db, "connection") and hasattr(self.db.connection, "cursor") and callable(self.db.connection.cursor):
                cursor = self.db.connection.cursor()
            elif hasattr(self.db, "cursor") and callable(self.db.cursor):
                cursor = self.db.cursor()
            else:
                raise AttributeError("El objeto de base de datos no proporciona un cursor válido mediante 'cursor()' o 'connection.cursor()'.")
            
            query = """
                INSERT INTO payments (student_id, amount, description, payment_date)
                VALUES (?, ?, ?, ?)
            """
            payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(query, (student_id, amount, description, payment_date))
            
            if hasattr(self.db, "commit") and callable(self.db.commit):
                self.db.commit()
            elif hasattr(self.db, "connection") and hasattr(self.db.connection, "commit") and callable(self.db.connection.commit):
                self.db.connection.commit()
            else:
                print("Advertencia: No se encontró método commit, verifique la configuración de la base de datos.")
            
            receipt_number = cursor.lastrowid
            return True, "Pago registrado exitosamente.", receipt_number, payment_date

        except Exception as e:
            detailed_error = traceback.format_exc()
            print("Error al registrar el pago:")
            print(detailed_error)
            return False, f"Error al registrar el pago: {e}", None, None

    def get_payments_by_student_identification(self, student_id):
        """
        Retrieves all payment records for a given student_id.
        Returns a list of sqlite3.Row objects.
        """
        try:
            if hasattr(self.db, "connection") and hasattr(self.db.connection, "cursor") and callable(self.db.connection.cursor):
                cursor = self.db.connection.cursor()
            elif hasattr(self.db, "cursor") and callable(self.db.cursor):
                cursor = self.db.cursor()
            else:
                raise AttributeError("El objeto de base de datos no proporciona un cursor válido mediante 'cursor()' o 'connection.cursor()'.")
            
            query = "SELECT * FROM payments WHERE student_id = ?"
            cursor.execute(query, (student_id,))
            return cursor.fetchall()
        except Exception as e:
            detailed_error = traceback.format_exc()
            print(f"Error fetching payments for student {student_id}:")
            print(detailed_error)
            return []

    def get_payment_by_id(self, payment_id):
        """
        Retrieves a single payment record by its payment id.
        Returns a sqlite3.Row object.
        """
        try:
            if hasattr(self.db, "connection") and hasattr(self.db.connection, "cursor") and callable(self.db.connection.cursor):
                cursor = self.db.connection.cursor()
            elif hasattr(self.db, "cursor") and callable(self.db.cursor):
                cursor = self.db.cursor()
            else:
                raise AttributeError("El objeto de base de datos no proporciona un cursor válido mediante 'cursor()' o 'connection.cursor()'.")
            
            query = "SELECT * FROM payments WHERE id = ?"
            cursor.execute(query, (payment_id,))
            return cursor.fetchone()
        except Exception as e:
            detailed_error = traceback.format_exc()
            print(f"Error fetching payment with id {payment_id}:")
            print(detailed_error)
            return None
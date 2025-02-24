import sqlite3
import traceback
from datetime import datetime

class PaymentController:
    def __init__(self, db):
        """
        Inicializa el PaymentController con un objeto de base de datos.
        Se asegura de que la tabla 'payments' exista, incluyendo la columna enrollment_id.
        """
        self.db = db
        self.cursor = self._get_cursor()
        self.initialize_payments_table()

    def _get_cursor(self):
        if hasattr(self.db, "cursor") and callable(self.db.cursor):
            return self.db.cursor()
        elif hasattr(self.db, "connection") and hasattr(self.db.connection, "cursor") and callable(self.db.connection.cursor):
            return self.db.connection.cursor()
        else:
            raise AttributeError("El objeto de base de datos no proporciona un cursor válido.")

    def _commit(self):
        if hasattr(self.db, "commit") and callable(self.db.commit):
            self.db.commit()
        elif hasattr(self.db, "connection") and hasattr(self.db.connection, "commit") and callable(self.db.connection.commit):
            self.db.connection.commit()
        else:
            print("Advertencia: No se encontró método commit, verifique la configuración de la base de datos.")

    def initialize_payments_table(self):
        """
        Crea la tabla 'payments' si no existe.
        Ahora se incluye la columna enrollment_id para vincular el pago a una inscripción.
        """
        try:
            create_table_query = """
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    enrollment_id INTEGER,
                    amount REAL,
                    description TEXT,
                    payment_date TEXT,
                    receipt_number INTEGER,
                    FOREIGN KEY(enrollment_id) REFERENCES enrollments(id)
                )
            """
            self.cursor.execute(create_table_query)
            self._commit()
        except Exception as e:
            detailed_error = traceback.format_exc()
            print("Error al inicializar la tabla 'payments':")
            print(detailed_error)

    def register_payment(self, student_id, amount, description, enrollment_id=None):
        """
        Inserta un nuevo registro de pago en la tabla payments.
        Se asocia opcionalmente a una inscripción mediante enrollment_id.
        Retorna una tupla: (éxito, mensaje, receipt_number, payment_date).
        """
        try:
            payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            query = """
                INSERT INTO payments (student_id, enrollment_id, amount, description, payment_date)
                VALUES (?, ?, ?, ?, ?)
            """
            self.cursor.execute(query, (student_id, enrollment_id, amount, description, payment_date))
            self._commit()
            receipt_number = self.cursor.lastrowid
            update_query = "UPDATE payments SET receipt_number = ? WHERE id = ?"
            self.cursor.execute(update_query, (receipt_number, receipt_number))
            self._commit()
            return True, "Pago registrado exitosamente.", receipt_number, payment_date
        except Exception as e:
            detailed_error = traceback.format_exc()
            print("Error al registrar el pago:")
            print(detailed_error)
            return False, f"Error al registrar el pago: {e}", None, None

    def get_payments_by_student(self, student_id):
        """
        Recupera todos los registros de pago para un determinado student_id, ordenados por fecha descendente.
        """
        try:
            query = "SELECT * FROM payments WHERE student_id = ? ORDER BY payment_date DESC"
            self.cursor.execute(query, (student_id,))
            return self.cursor.fetchall()
        except Exception as e:
            detailed_error = traceback.format_exc()
            print(f"Error fetching payments for student {student_id}:")
            print(detailed_error)
            return []

    def get_payment_by_id(self, payment_id):
        """
        Recupera un registro de pago individual por su id.
        """
        try:
            query = "SELECT * FROM payments WHERE id = ?"
            self.cursor.execute(query, (payment_id,))
            return self.cursor.fetchone()
        except Exception as e:
            detailed_error = traceback.format_exc()
            print(f"Error fetching payment with id {payment_id}:")
            print(detailed_error)
            return None

# src/controllers/payment_controller.py
import sqlite3
import traceback
from datetime import datetime
from src.utils.db_utils import db_cursor

class PaymentController:
    def __init__(self, db):
        """
        Inicializa el PaymentController con un objeto de base de datos.
        Se asegura de que la tabla 'payments' exista, incluyendo la columna enrollment_id.
        """
        self.db = db
        self.initialize_payments_table()

    def initialize_payments_table(self):
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
            with db_cursor(self.db) as cursor:
                cursor.execute(create_table_query)
        except Exception as e:
            detailed_error = traceback.format_exc()
            print("Error al inicializar la tabla 'payments':")
            print(detailed_error)

    def register_payment(self, student_id, amount, description, enrollment_id=None):
        try:
            payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            query = """
                INSERT INTO payments (student_id, enrollment_id, amount, description, payment_date)
                VALUES (?, ?, ?, ?, ?)
            """
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (student_id, enrollment_id, amount, description, payment_date))
                receipt_number = cursor.lastrowid
                update_query = "UPDATE payments SET receipt_number = ? WHERE id = ?"
                cursor.execute(update_query, (receipt_number, receipt_number))
            return True, "Pago registrado exitosamente.", receipt_number, payment_date
        except Exception as e:
            detailed_error = traceback.format_exc()
            print("Error al registrar el pago:")
            print(detailed_error)
            return False, f"Error al registrar el pago: {e}", None, None

    def get_payments_by_student(self, student_id):
        try:
            query = "SELECT * FROM payments WHERE student_id = ? ORDER BY payment_date DESC"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (student_id,))
                return cursor.fetchall()
        except Exception as e:
            detailed_error = traceback.format_exc()
            print(f"Error fetching payments for student {student_id}:")
            print(detailed_error)
            return []

    def get_payment_by_id(self, payment_id):
        try:
            query = "SELECT * FROM payments WHERE id = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (payment_id,))
                return cursor.fetchone()
        except Exception as e:
            detailed_error = traceback.format_exc()
            print(f"Error fetching payment with id {payment_id}:")
            print(detailed_error)
            return None

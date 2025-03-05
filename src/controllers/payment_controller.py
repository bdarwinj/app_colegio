# src/controllers/payment_controller.py
import sqlite3
from datetime import datetime
from src.utils.db_utils import db_cursor
from src.logger import logger

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
                    receipt_number TEXT,
                    FOREIGN KEY(enrollment_id) REFERENCES enrollments(id)
                )
            """
            with db_cursor(self.db) as cursor:
                cursor.execute(create_table_query)
        except Exception as e:
            logger.exception("Error al inicializar la tabla 'payments'")

    def _format_receipt(self, payment_date, raw_receipt):
        """
        Formatea el número de recibo utilizando la fecha del pago y el id generado.
        """
        dt = datetime.strptime(payment_date, "%Y-%m-%d %H:%M:%S")
        date_part = dt.strftime("%Y%m%d")
        return f"{date_part}-{int(raw_receipt):04d}"

    def register_payment(self, student_id, amount, description, enrollment_id=None):
        try:
            payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            query = """
                INSERT INTO payments (student_id, enrollment_id, amount, description, payment_date)
                VALUES (?, ?, ?, ?, ?)
            """
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (student_id, enrollment_id, amount, description, payment_date))
                raw_receipt = cursor.lastrowid
                formatted_receipt = self._format_receipt(payment_date, raw_receipt)
                update_query = "UPDATE payments SET receipt_number = ? WHERE id = ?"
                cursor.execute(update_query, (formatted_receipt, raw_receipt))
            return True, "Pago registrado exitosamente.", formatted_receipt, payment_date
        except Exception as e:
            logger.exception("Error al registrar el pago")
            return False, f"Error al registrar el pago: {e}", None, None

    def _execute_fetchall(self, query, params=(), error_message="Error al ejecutar consulta"):
        """
        Ejecuta una consulta que retorna múltiples filas.
        """
        try:
            with db_cursor(self.db) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logger.exception(error_message)
            return []

    def _execute_fetchone(self, query, params=(), error_message="Error al ejecutar consulta"):
        """
        Ejecuta una consulta que retorna una única fila.
        """
        try:
            with db_cursor(self.db) as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()
        except Exception as e:
            logger.exception(error_message)
            return None

    def get_payments_by_student(self, student_id):
        query = "SELECT * FROM payments WHERE student_id = ? ORDER BY payment_date DESC"
        return self._execute_fetchall(query, (student_id,), f"Error al obtener pagos para el estudiante {student_id}")

    def get_payment_by_id(self, payment_id):
        query = "SELECT * FROM payments WHERE id = ?"
        return self._execute_fetchone(query, (payment_id,), f"Error al obtener el pago con id {payment_id}")

    def get_payments_in_month(self, year_month_str):
        """
        Obtiene todos los pagos realizados en un mes específico, en formato 'YYYY-MM'.
        Ejemplo: '2025-03'.
        """
        query = """
                SELECT * FROM payments
                WHERE strftime('%Y-%m', payment_date) = ?
            """
        return self._execute_fetchall(query, (year_month_str,), "Error al obtener pagos del mes")

    def get_payments_in_year(self, year):
        """
        Obtiene todos los pagos realizados en un año específico.
        Ejemplo: 2025.
        """
        query = """
                SELECT * FROM payments
                WHERE strftime('%Y', payment_date) = ?
            """
        return self._execute_fetchall(query, (str(year),), "Error al obtener pagos del año")

import sqlite3
import traceback

class StudentController:
    def __init__(self, db):
        self.db = db
        # No se llama a initialize_students_table() porque la tabla ya está en database.py

    def _get_cursor(self):
        """Helper method to obtain a valid cursor."""
        try:
            if hasattr(self.db, "cursor") and callable(self.db.cursor):
                return self.db.cursor()
            elif hasattr(self.db, "connection") and hasattr(self.db.connection, "cursor") and callable(self.db.connection.cursor):
                return self.db.connection.cursor()
            else:
                raise AttributeError("Database object does not have a 'cursor' method.")
        except AttributeError as e:
            raise

    def _execute_and_commit(self, query, params=None):
        """Ejecuta una consulta y realiza commit si es posible."""
        try:
            cursor = self._get_cursor()
            cursor.execute(query, params or ())
            if hasattr(self.db, "commit") and callable(self.db.commit):
                self.db.commit()
            elif hasattr(self.db, "connection") and hasattr(self.db.connection, "commit") and callable(self.db.connection.commit):
                self.db.connection.commit()
            return True
        except sqlite3.Error as e:
            traceback.print_exc()
            return False

    def get_student_by_identification(self, identificacion):
        cursor = self._get_cursor()
        query = "SELECT * FROM estudiantes WHERE identificacion = ?"
        cursor.execute(query, (identificacion,))
        return cursor.fetchone()

    def get_all_students(self):
        cursor = self._get_cursor()
        query = "SELECT * FROM estudiantes"
        cursor.execute(query)
        return cursor.fetchall() or []

    def delete_student(self, identificacion):
        if not self.get_student_by_identification(identificacion):
            return False, "Estudiante no encontrado."
        query = "DELETE FROM estudiantes WHERE identificacion = ?"
        if self._execute_and_commit(query, (identificacion,)):
            return True, "Estudiante eliminado correctamente."
        return False, "Error al eliminar el estudiante."

    def deactivate_student(self, identificacion):
        if not self.get_student_by_identification(identificacion):
            return False, "Estudiante no encontrado."
        query = "UPDATE estudiantes SET active = 0 WHERE identificacion = ?"
        if self._execute_and_commit(query, (identificacion,)):
            return True, "Estudiante desactivado correctamente."
        return False, "Error al desactivar el estudiante."

    def register_student(self, identificacion, nombre, apellido, course_id, representante, telefono):
        query = """
            INSERT INTO estudiantes (identificacion, nombre, apellido, course_id, representante, telefono, active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """
        if self._execute_and_commit(query, (identificacion, nombre, apellido, course_id, representante, telefono)):
            return True, "Estudiante registrado correctamente."
        return False, "Error al registrar el estudiante."

    def get_all_configs(self):
        try:
            cursor = self._get_cursor()
            query = "SELECT key, value FROM config"  # Corregido de 'configuraciones' a 'config'
            cursor.execute(query)
            rows = cursor.fetchall()
            return {key: value for key, value in rows}
        except Exception:
            traceback.print_exc()
            return {
                "SCHOOL_NAME": "Nombre del Colegio",
                "LOGO_PATH": "D:\\laragon\\www\\colegio_app\\assets\\logo.png"
            }

    def get_payments_by_student(self, student_identificacion):
        """
        Retorna una lista de pagos asociados al estudiante.
        Cada pago se devuelve como un diccionario con la clave "amount".
        """
        try:
            # Obtener el id del estudiante usando su identificación
            query_student = "SELECT id FROM estudiantes WHERE identificacion = ?"
            self.db.cursor.execute(query_student, (student_identificacion,))
            student_record = self.db.cursor.fetchone()
            if not student_record:
                return []

            student_id = student_record["id"]

            # Consultar los pagos asociados al id del estudiante
            query_payments = "SELECT monto FROM pagos WHERE estudiante_id = ?"
            self.db.cursor.execute(query_payments, (student_id,))
            results = self.db.cursor.fetchall()
            payments = [{"amount": row["monto"]} for row in results]
            return payments

        except Exception as e:
            print(f"Error al obtener pagos del estudiante: {e}")
            return []
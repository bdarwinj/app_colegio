# src/controllers/student_controller.py
import sqlite3
from src.utils.db_utils import db_cursor
from src.logger import logger

class StudentController:
    def __init__(self, db):
        """
        Inicializa el controlador de estudiantes.
        :param db: Instancia de base de datos o conexión.
        """
        self.db = db

    def _execute_and_commit(self, query, params=None):
        try:
            with db_cursor(self.db) as cursor:
                cursor.execute(query, params or ())
            return True
        except sqlite3.Error as e:
            logger.exception("Error al ejecutar y confirmar la consulta")
            return False

    def get_student_by_identification(self, identificacion):
        try:
            query = "SELECT * FROM estudiantes WHERE identificacion = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (identificacion,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            logger.exception("Error en get_student_by_identification")
            return None

    def get_student_by_id(self, student_id):
        try:
            query = "SELECT * FROM estudiantes WHERE id = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (student_id,))
                row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.exception(f"Error al obtener el estudiante con ID {student_id}")
            return None

    def get_course_name(self, course_id):
        if course_id is None:
            return "N/A"
        try:
            query = "SELECT name, seccion FROM courses WHERE id = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (course_id,))
                result = cursor.fetchone()
            if result:
                name = result[0]
                seccion = result[1] if len(result) > 1 and result[1] else ""
                return f"{name} - {seccion}" if seccion.strip() else name
            return "N/A"
        except sqlite3.Error as e:
            logger.exception("Error en get_course_name")
            return "N/A"

    def get_all_students(self):
        try:
            query = "SELECT id, identificacion, nombre, apellido, course_id, representante, telefono, active FROM estudiantes"
            with db_cursor(self.db) as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
            return [{
                "id": row[0],
                "identificacion": row[1],
                "nombre": row[2],
                "apellido": row[3],
                "course_name": self.get_course_name(row[4]),
                "representante": row[5],
                "telefono": row[6],
                "active": row[7]
            } for row in rows] if rows else []
        except sqlite3.Error as e:
            logger.exception("Error en get_all_students")
            return []

    def delete_student(self, identificacion):
        if not self.get_student_by_identification(identificacion):
            return False, "Estudiante no encontrado."
        try:
            query = "DELETE FROM estudiantes WHERE identificacion = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (identificacion,))
            return True, "Estudiante eliminado correctamente."
        except Exception as e:
            logger.exception("Error al eliminar el estudiante")
            return False, "Error al eliminar el estudiante."

    def deactivate_student(self, identificacion):
        if not self.get_student_by_identification(identificacion):
            return False, "Estudiante no encontrado."
        try:
            query = "UPDATE estudiantes SET active = 0 WHERE identificacion = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (identificacion,))
            return True, "Estudiante desactivado correctamente."
        except Exception as e:
            logger.exception("Error al desactivar el estudiante")
            return False, "Error al desactivar el estudiante."

    def register_student(self, identificacion, nombre, apellido, course_id, representante, telefono):
        if not identificacion or not identificacion.isdigit():
            return False, "El número de identificación debe ser numérico y no vacío."
        if not nombre or not isinstance(nombre, str):
            return False, "El nombre debe ser una cadena no vacía."
        if not apellido or not isinstance(apellido, str):
            return False, "El apellido debe ser una cadena no vacía."
        query = """
            INSERT INTO estudiantes (identificacion, nombre, apellido, course_id, representante, telefono, active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """
        try:
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (identificacion, nombre, apellido, course_id, representante, telefono))
            return True, "Estudiante registrado correctamente."
        except Exception as e:
            logger.exception("Error al registrar el estudiante")
            return False, "Error al registrar el estudiante."

    def get_payments_by_student(self, student_identificacion):
        try:
            query = "SELECT id FROM estudiantes WHERE identificacion = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (student_identificacion,))
                student_record = cursor.fetchone()
            if not student_record:
                return []
            student_id = student_record[0]
            query = "SELECT amount FROM payments WHERE student_id = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (student_id,))
                rows = cursor.fetchall()
            return [{"amount": row[0]} for row in rows] if rows else []
        except Exception as e:
            logger.exception("Error al obtener pagos por estudiante")
            return []

    def update_student_course(self, student_id, new_course_id):
        try:
            query = "UPDATE estudiantes SET course_id = ? WHERE id = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (new_course_id, student_id))
            return True, "Curso actualizado correctamente."
        except Exception as e:
            logger.exception("Error al actualizar el curso del estudiante")
            return False, f"Error al actualizar el curso: {e}"

# src/controllers/student_controller.py
import sqlite3
import traceback
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

    def _execute_fetchone(self, query, params=(), error_context="Error al ejecutar consulta"):
        try:
            with db_cursor(self.db) as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()
        except Exception as e:
            logger.exception(error_context)
            return None

    def _execute_fetchall(self, query, params=(), error_context="Error al ejecutar consulta"):
        try:
            with db_cursor(self.db) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logger.exception(error_context)
            return []

    def get_student_by_identification(self, identificacion):
        query = "SELECT * FROM estudiantes WHERE identificacion = ?"
        return self._execute_fetchone(query, (identificacion,), "Error en get_student_by_identification")

    def get_student_by_id(self, student_id):
        query = "SELECT * FROM estudiantes WHERE id = ?"
        row = self._execute_fetchone(query, (student_id,), f"Error al obtener el estudiante con ID {student_id}")
        return dict(row) if row else None

    def get_course_name(self, course_id):
        if course_id is None:
            return "N/A"
        query = "SELECT name, seccion FROM courses WHERE id = ?"
        result = self._execute_fetchone(query, (course_id,), "Error en get_course_name")
        if result:
            name = result[0]
            seccion = result[1] if len(result) > 1 and result[1] else ""
            return f"{name} - {seccion}" if seccion.strip() else name
        return "N/A"

    def get_all_students(self):
        query = ("SELECT id, identificacion, nombre, apellido, course_id, "
                 "representante, telefono, active FROM estudiantes")
        rows = self._execute_fetchall(query, (), "Error en get_all_students")
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

    def register_student(self, identificacion, nombre, apellido, course_id, representante, telefono, email):
        if not identificacion or not identificacion.isdigit():
            return False, "El número de identificación debe ser numérico y no vacío."
        if not nombre or not isinstance(nombre, str):
            return False, "El nombre debe ser una cadena no vacía."
        if not apellido or not isinstance(apellido, str):
            return False, "El apellido debe ser una cadena no vacía."
        query = """
            INSERT INTO estudiantes (identificacion, nombre, apellido, course_id, representante, telefono, email, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """
        if self._execute_and_commit(query, (identificacion, nombre, apellido, course_id, representante, telefono, email)):
            return True, "Estudiante registrado correctamente."
        return False, "Error al registrar el estudiante."

    def get_payments_by_student(self, student_identificacion):
        query = "SELECT id FROM estudiantes WHERE identificacion = ?"
        student_record = self._execute_fetchone(query, (student_identificacion,),
                                                  "Error al obtener estudiante por identificación")
        if not student_record:
            return []
        student_id = student_record[0]
        query = "SELECT amount FROM payments WHERE student_id = ?"
        rows = self._execute_fetchall(query, (student_id,), "Error al obtener pagos por estudiante")
        return [{"amount": row[0]} for row in rows] if rows else []

    def update_student_course(self, student_id, new_course_id):
        query = "UPDATE estudiantes SET course_id = ? WHERE id = ?"
        if self._execute_and_commit(query, (new_course_id, student_id)):
            return True, "Curso actualizado correctamente."
        return False, "Error al actualizar el curso del estudiante."
    
    def update_student_info(self, student_id, new_course_id, new_representative, new_phone):
        """
        Actualiza el curso, el nombre del representante y el teléfono del representante para un estudiante.
        """
        query = "UPDATE estudiantes SET course_id = ?, representante = ?, telefono = ? WHERE id = ?"
        if self._execute_and_commit(query, (new_course_id, new_representative, new_phone, student_id)):
            return True, "Datos del estudiante actualizados correctamente."
        return False, "Error al actualizar la información del estudiante."

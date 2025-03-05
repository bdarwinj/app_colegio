# src/controllers/course_controller.py
from src.models.course import Course
import sqlite3
from src.utils.db_utils import db_cursor

# Constantes para estados
ACTIVE = 1
INACTIVE = 0

class CourseController:
    def __init__(self, db):
        """
        Inicializa el CourseController con un objeto de base de datos.
        
        :param db: Objeto de conexión a la base de datos.
        """
        self.db = db

    def _get_cursor(self):
        """
        Método auxiliar para obtener un cursor válido de la base de datos.
        (Se conserva para compatibilidad, pero no se usa en la refactorización).
        
        :return: Cursor de la base de datos.
        :raises AttributeError: Si el objeto de base de datos no tiene un método 'cursor'.
        """
        if hasattr(self.db, "cursor") and callable(self.db.cursor):
            return self.db.cursor()
        elif hasattr(self.db, "connection") and hasattr(self.db.connection, "cursor") and callable(self.db.connection.cursor):
            return self.db.connection.cursor()
        else:
            raise AttributeError("El objeto de base de datos no tiene un método 'cursor'.")

    def _execute_update(self, query, params, success_message, integrity_error_message=None, error_prefix="Error al ejecutar consulta: "):
        """
        Método auxiliar para ejecutar queries de actualización.
        """
        try:
            with db_cursor(self.db) as cursor:
                cursor.execute(query, params)
            return True, success_message
        except sqlite3.IntegrityError:
            return False, integrity_error_message if integrity_error_message else f"{error_prefix}integridad error."
        except sqlite3.Error as e:
            return False, f"{error_prefix}{e}"

    def _execute_fetchall(self, query, params=(), default_return=[]):
        """
        Método auxiliar para ejecutar queries que retornan múltiples filas.
        """
        try:
            with db_cursor(self.db) as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error:
            return default_return

    def _execute_fetchone(self, query, params, default_return=None):
        """
        Método auxiliar para ejecutar queries que retornan una sola fila.
        """
        try:
            with db_cursor(self.db) as cursor:
                cursor.execute(query, params)
                row = cursor.fetchone()
            return dict(row) if row else default_return
        except sqlite3.Error:
            return default_return

    def add_course(self, name, seccion=None):
        if not name or not isinstance(name, str):
            return False, "El nombre del curso debe ser una cadena no vacía."
        if seccion is not None and not isinstance(seccion, str):
            return False, "La sección debe ser una cadena."
        query = "INSERT INTO courses (name, seccion, active) VALUES (?, ?, ?)"
        return self._execute_update(
            query,
            (name, seccion or "", ACTIVE),
            "Curso agregado correctamente.",
            integrity_error_message="El curso con esa sección ya existe.",
            error_prefix="Error al agregar curso: "
        )

    def edit_course(self, course_id, new_name, new_seccion=None):
        if not isinstance(course_id, int):
            return False, "El ID del curso debe ser un entero."
        if not new_name or not isinstance(new_name, str):
            return False, "El nuevo nombre del curso debe ser una cadena no vacía."
        if new_seccion is not None and not isinstance(new_seccion, str):
            return False, "La nueva sección debe ser una cadena."
        query = "UPDATE courses SET name = ?, seccion = ? WHERE id = ?"
        return self._execute_update(
            query,
            (new_name, new_seccion or "", course_id),
            "Curso editado correctamente.",
            error_prefix="Error al editar curso: "
        )

    def deactivate_course(self, course_id):
        if not isinstance(course_id, int):
            return False, "El ID del curso debe ser un entero."
        query = "UPDATE courses SET active = ? WHERE id = ?"
        return self._execute_update(
            query,
            (INACTIVE, course_id),
            "Curso desactivado correctamente.",
            error_prefix="Error al desactivar curso: "
        )

    def get_active_courses(self):
        query = "SELECT * FROM courses WHERE active = ?"
        return self._execute_fetchall(query, (ACTIVE,), default_return=[])

    def get_all_courses(self):
        query = "SELECT * FROM courses"
        return self._execute_fetchall(query, default_return=[])

    def get_course_by_id(self, course_id):
        if not isinstance(course_id, int):
            return None
        query = "SELECT * FROM courses WHERE id = ?"
        return self._execute_fetchone(query, (course_id,), default_return=None)

    def get_courses_by_grade(self, grade):
        """
        Obtiene todos los cursos activos que coinciden con el nombre del grado especificado.
        
        :param grade: Nombre del grado (por ejemplo, "segundo").
        :return: Lista de cursos (diccionarios) que coinciden con el grado.
        """
        query = "SELECT * FROM courses WHERE name = ? AND active = ?"
        return self._execute_fetchall(query, (grade, ACTIVE), default_return=[])
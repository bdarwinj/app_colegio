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
        try:
            if hasattr(self.db, "cursor") and callable(self.db.cursor):
                return self.db.cursor()
            elif hasattr(self.db, "connection") and hasattr(self.db.connection, "cursor") and callable(self.db.connection.cursor):
                return self.db.connection.cursor()
            else:
                raise AttributeError("El objeto de base de datos no tiene un método 'cursor'.")
        except AttributeError as e:
            raise

    def add_course(self, name, seccion=None):
        if not name or not isinstance(name, str):
            return False, "El nombre del curso debe ser una cadena no vacía."
        if seccion is not None and not isinstance(seccion, str):
            return False, "La sección debe ser una cadena."
        try:
            query = "INSERT INTO courses (name, seccion, active) VALUES (?, ?, ?)"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (name, seccion or "", ACTIVE))
            return True, "Curso agregado correctamente."
        except sqlite3.IntegrityError:
            return False, "El curso con esa sección ya existe."
        except sqlite3.Error as e:
            return False, f"Error al agregar curso: {e}"

    def edit_course(self, course_id, new_name, new_seccion=None):
        if not isinstance(course_id, int):
            return False, "El ID del curso debe ser un entero."
        if not new_name or not isinstance(new_name, str):
            return False, "El nuevo nombre del curso debe ser una cadena no vacía."
        if new_seccion is not None and not isinstance(new_seccion, str):
            return False, "La nueva sección debe ser una cadena."
        try:
            query = "UPDATE courses SET name = ?, seccion = ? WHERE id = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (new_name, new_seccion or "", course_id))
            return True, "Curso editado correctamente."
        except sqlite3.Error as e:
            return False, f"Error al editar curso: {e}"

    def deactivate_course(self, course_id):
        if not isinstance(course_id, int):
            return False, "El ID del curso debe ser un entero."
        try:
            query = "UPDATE courses SET active = ? WHERE id = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (INACTIVE, course_id))
            return True, "Curso desactivado correctamente."
        except sqlite3.Error as e:
            return False, f"Error al desactivar curso: {e}"

    def get_active_courses(self):
        try:
            query = "SELECT * FROM courses WHERE active = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (ACTIVE,))
                rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            return []

    def get_all_courses(self):
        try:
            query = "SELECT * FROM courses"
            with db_cursor(self.db) as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            return []

    def get_course_by_id(self, course_id):
        if not isinstance(course_id, int):
            return None
        try:
            query = "SELECT * FROM courses WHERE id = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (course_id,))
                course_data = cursor.fetchone()
            if course_data:
                return dict(course_data)
            return None
        except sqlite3.Error as e:
            return None

    def get_courses_by_grade(self, grade):
        """
        Obtiene todos los cursos activos que coinciden con el nombre del grado especificado.
        
        :param grade: Nombre del grado (por ejemplo, "segundo").
        :return: Lista de cursos (diccionarios) que coinciden con el grado.
        """
        try:
            query = "SELECT * FROM courses WHERE name = ? AND active = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (grade, ACTIVE))
                rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            return []

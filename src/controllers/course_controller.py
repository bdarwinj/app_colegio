from src.models.course import Course
import sqlite3

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
        self.cursor = self._get_cursor()  # Cursor persistente inicializado aquí

    def _get_cursor(self):
        """
        Método auxiliar para obtener un cursor válido de la base de datos.
        
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
        """
        Agrega un nuevo curso a la base de datos.
        
        :param name: Nombre del curso a agregar (por ejemplo, "Tercero").
        :param seccion: Sección del curso (por ejemplo, "A", "B"). Opcional.
        :return: Tupla (éxito: bool, mensaje: str)
        """
        if not name or not isinstance(name, str):
            return False, "El nombre del curso debe ser una cadena no vacía."
        if seccion is not None and not isinstance(seccion, str):
            return False, "La sección debe ser una cadena."
        try:
            # Insertar curso con estado activo por defecto
            query = "INSERT INTO courses (name, seccion, active) VALUES (?, ?, ?)"
            self.cursor.execute(query, (name, seccion or "", ACTIVE))
            self.db.connection.commit()
            return True, "Curso agregado correctamente."
        except sqlite3.IntegrityError:
            return False, "El curso con esa sección ya existe."
        except sqlite3.Error as e:
            return False, f"Error al agregar curso: {e}"

    def edit_course(self, course_id, new_name, new_seccion=None):
        """
        Edita el nombre y la sección de un curso existente.
        
        :param course_id: ID del curso a editar.
        :param new_name: Nuevo nombre para el curso.
        :param new_seccion: Nueva sección para el curso. Opcional.
        :return: Tupla (éxito: bool, mensaje: str)
        """
        if not isinstance(course_id, int):
            return False, "El ID del curso debe ser un entero."
        if not new_name or not isinstance(new_name, str):
            return False, "El nuevo nombre del curso debe ser una cadena no vacía."
        if new_seccion is not None and not isinstance(new_seccion, str):
            return False, "La nueva sección debe ser una cadena."
        try:
            query = "UPDATE courses SET name = ?, seccion = ? WHERE id = ?"
            self.cursor.execute(query, (new_name, new_seccion or "", course_id))
            self.db.connection.commit()
            return True, "Curso editado correctamente."
        except sqlite3.Error as e:
            return False, f"Error al editar curso: {e}"

    def deactivate_course(self, course_id):
        """
        Desactiva un curso cambiando su estado a 0.
        
        :param course_id: ID del curso a desactivar.
        :return: Tupla (éxito: bool, mensaje: str)
        """
        if not isinstance(course_id, int):
            return False, "El ID del curso debe ser un entero."
        try:
            query = "UPDATE courses SET active = ? WHERE id = ?"
            self.cursor.execute(query, (INACTIVE, course_id))
            self.db.connection.commit()
            return True, "Curso desactivado correctamente."
        except sqlite3.Error as e:
            return False, f"Error al desactivar curso: {e}"

    def get_active_courses(self):
        """
        Obtiene todos los cursos activos.
        
        :return: Lista de diccionarios con los datos de los cursos activos.
        """
        try:
            query = "SELECT * FROM courses WHERE active = ?"
            self.cursor.execute(query, (ACTIVE,))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            return []

    def get_all_courses(self):
        """
        Obtiene todos los cursos, activos e inactivos.
        
        :return: Lista de diccionarios con los datos de todos los cursos.
        """
        try:
            query = "SELECT * FROM courses"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            return []

    def get_course_by_id(self, course_id):
        """
        Obtiene un curso por su ID.
        
        :param course_id: ID del curso a obtener.
        :return: Diccionario con los datos del curso o None si no se encuentra.
        """
        if not isinstance(course_id, int):
            return None
        try:
            query = "SELECT * FROM courses WHERE id = ?"
            self.cursor.execute(query, (course_id,))
            course_data = self.cursor.fetchone()
            if course_data:
                return dict(course_data)
            return None
        except sqlite3.Error as e:
            return None  # Devolver None en lugar de imprimir el error

    def get_courses_by_grade(self, grade):
        """
        Obtiene todos los cursos activos que coinciden con el nombre del grado especificado.
        
        :param grade: Nombre del grado (por ejemplo, "segundo").
        :return: Lista de cursos (diccionarios) que coinciden con el grado.
        """
        try:
            query = "SELECT * FROM courses WHERE name = ? AND active = ?"
            self.cursor.execute(query, (grade, ACTIVE))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            return []
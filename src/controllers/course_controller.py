from src.models.course import Course

class CourseController:
    def __init__(self, db):
        """
        Inicializa el CourseController con un objeto de base de datos.
        
        :param db: Objeto de conexión a la base de datos.
        """
        self.db = db

    def add_course(self, name):
        """
        Agrega un nuevo curso a la base de datos.
        
        :param name: Nombre del curso a agregar.
        :return: Tupla (éxito: bool, mensaje: str)
        """
        if not name or not isinstance(name, str):
            return False, "El nombre del curso debe ser una cadena no vacía."
        try:
            query = "INSERT INTO courses (name, active) VALUES (?, 1)"
            self.db.cursor.execute(query, (name,))
            self.db.connection.commit()
            return True, "Curso agregado correctamente."
        except Exception as e:
            return False, f"Error al agregar curso: {e}"

    def edit_course(self, course_id, new_name):
        """
        Edita el nombre de un curso existente.
        
        :param course_id: ID del curso a editar.
        :param new_name: Nuevo nombre para el curso.
        :return: Tupla (éxito: bool, mensaje: str)
        """
        if not new_name or not isinstance(new_name, str):
            return False, "El nuevo nombre del curso debe ser una cadena no vacía."
        try:
            query = "UPDATE courses SET name = ? WHERE id = ?"
            self.db.cursor.execute(query, (new_name, course_id))
            self.db.connection.commit()
            return True, "Curso editado correctamente."
        except Exception as e:
            return False, f"Error al editar curso: {e}"

    def deactivate_course(self, course_id):
        """
        Desactiva un curso cambiando su estado a 0.
        
        :param course_id: ID del curso a desactivar.
        :return: Tupla (éxito: bool, mensaje: str)
        """
        try:
            query = "UPDATE courses SET active = 0 WHERE id = ?"
            self.db.cursor.execute(query, (course_id,))
            self.db.connection.commit()
            return True, "Curso desactivado correctamente."
        except Exception as e:
            return False, f"Error al desactivar curso: {e}"

    def get_active_courses(self):
        """
        Obtiene todos los cursos activos.
        
        :return: Lista de cursos activos.
        """
        try:
            query = "SELECT * FROM courses WHERE active = 1"
            self.db.cursor.execute(query)
            return self.db.cursor.fetchall()
        except Exception as e:
            return []

    def get_all_courses(self):
        """
        Obtiene todos los cursos, activos e inactivos.
        
        :return: Lista de todos los cursos.
        """
        try:
            query = "SELECT * FROM courses"
            self.db.cursor.execute(query)
            return self.db.cursor.fetchall()
        except Exception as e:
            return []

    def get_course_by_id(self, course_id):
        """
        Obtiene un curso por su ID.
        
        :param course_id: ID del curso a obtener.
        :return: Diccionario con los datos del curso o None si no se encuentra.
        """
        try:
            query = "SELECT * FROM courses WHERE id = ?"
            self.db.cursor.execute(query, (course_id,))
            course_data = self.db.cursor.fetchone()
            if course_data:
                return dict(course_data)
            return None
        except Exception as e:
            print(f"Error al obtener el curso: {e}")
            return None
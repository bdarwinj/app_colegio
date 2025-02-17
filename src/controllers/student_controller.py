import sqlite3
import traceback

class StudentController:
    def __init__(self, db):
        self.db = db
        self.initialize_students_table()
    
    def _get_cursor(self):
        """
        Helper method to obtain a valid cursor.
        If self.db has a callable cursor(), use it.
        Else if self.db has a 'connection' attribute with a cursor() method, use that.
        Otherwise, raise an exception.
        """
        try:
            if hasattr(self.db, "cursor") and callable(self.db.cursor):
                return self.db.cursor()
            elif hasattr(self.db, "connection") and hasattr(self.db.connection, "cursor") and callable(self.db.connection.cursor):
                return self.db.connection.cursor()
            else:
                raise Exception("El objeto Database no tiene un método 'cursor'.")
        except Exception as e:
            raise Exception("No se pudo obtener un cursor válido de la base de datos.") from e

    def initialize_students_table(self):
        try:
            cursor = self._get_cursor()
            create_table_query = """
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    identificacion TEXT UNIQUE,
                    nombre TEXT,
                    apellido TEXT,
                    course_name TEXT,
                    representante TEXT,
                    telefono TEXT,
                    active INTEGER DEFAULT 1
                )
            """
            cursor.execute(create_table_query)
            # Use 'commit' from db or from db.connection if available
            if hasattr(self.db, "commit") and callable(self.db.commit):
                self.db.commit()
            elif hasattr(self.db, "connection") and hasattr(self.db.connection, "commit") and callable(self.db.connection.commit):
                self.db.connection.commit()
        except Exception as e:
            detailed_error = traceback.format_exc()
            print("Error al inicializar la tabla 'students':")
            print(detailed_error)

    def get_student_by_identification(self, identificacion):
        try:
            cursor = self._get_cursor()
            query = "SELECT * FROM students WHERE identificacion = ?"
            cursor.execute(query, (identificacion,))
            return cursor.fetchone()
        except Exception as e:
            detailed_error = traceback.format_exc()
            print("Error al obtener el estudiante:")
            print(detailed_error)
            return None

    def get_all_students(self):
        """
        Retorna una lista de todos los estudiantes.
        """
        try:
            cursor = self._get_cursor()
            query = "SELECT * FROM students"
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            detailed_error = traceback.format_exc()
            print("Error al obtener todos los estudiantes:")
            print(detailed_error)
            return []

    def delete_student(self, identificacion):
        """
        Elimina el estudiante con la identificación dada.
        Retorna una tupla: (éxito, mensaje).
        """
        try:
            student = self.get_student_by_identification(identificacion)
            if not student:
                return (False, "Estudiante no encontrado.")
            cursor = self._get_cursor()
            query = "DELETE FROM students WHERE identificacion = ?"
            cursor.execute(query, (identificacion,))
            if hasattr(self.db, "commit") and callable(self.db.commit):
                self.db.commit()
            elif hasattr(self.db, "connection") and hasattr(self.db.connection, "commit") and callable(self.db.connection.commit):
                self.db.connection.commit()
            return (True, "Estudiante eliminado correctamente.")
        except Exception as e:
            detailed_error = traceback.format_exc()
            print("Error al eliminar el estudiante:")
            print(detailed_error)
            return (False, f"Error al eliminar el estudiante: {e}")

    def deactivate_student(self, identificacion):
        """
        Desactiva el estudiante con la identificación dada.
        Retorna una tupla: (éxito, mensaje).
        """
        try:
            student = self.get_student_by_identification(identificacion)
            if not student:
                return (False, "Estudiante no encontrado.")
            cursor = self._get_cursor()
            query = "UPDATE students SET active = 0 WHERE identificacion = ?"
            cursor.execute(query, (identificacion,))
            if hasattr(self.db, "commit") and callable(self.db.commit):
                self.db.commit()
            elif hasattr(self.db, "connection") and hasattr(self.db.connection, "commit") and callable(self.db.connection.commit):
                self.db.connection.commit()
            return (True, "Estudiante desactivado correctamente.")
        except Exception as e:
            detailed_error = traceback.format_exc()
            print("Error al desactivar el estudiante:")
            print(detailed_error)
            return (False, f"Error al desactivar el estudiante: {e}")

    def register_student(self, identificacion, nombre, apellido, course_name, representante, telefono):
        try:
            cursor = self._get_cursor()
            query = """
                INSERT INTO students (identificacion, nombre, apellido, course_name, representante, telefono, active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """
            cursor.execute(query, (identificacion, nombre, apellido, course_name, representante, telefono))
            if hasattr(self.db, "commit") and callable(self.db.commit):
                self.db.commit()
            elif hasattr(self.db, "connection") and hasattr(self.db.connection, "commit") and callable(self.db.connection.commit):
                self.db.connection.commit()
            return (True, "Estudiante registrado correctamente.")
        except Exception as e:
            detailed_error = traceback.format_exc()
            print("Error al registrar el estudiante:")
            print(detailed_error)
            return (False, f"Error al registrar el estudiante: {e}")

    def get_all_configs(self):
        """
        Método de ejemplo para retornar configuraciones.
        Retorna un diccionario con configuraciones como SCHOOL_NAME y LOGO_PATH.
        """
        return {
            "SCHOOL_NAME": "Colegio Ejemplo",
            "LOGO_PATH": "path/to/logo.png"
        }
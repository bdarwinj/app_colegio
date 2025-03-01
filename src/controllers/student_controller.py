import sqlite3
import traceback

class StudentController:
    def __init__(self, db):
        """
        Inicializa el controlador de estudiantes.
        :param db: Instancia de base de datos o conexión.
        """
        self.db = db
        self.cursor = self._get_cursor()

    def _get_cursor(self):
        """
        Método auxiliar para obtener un cursor válido.
        :return: Cursor de la conexión SQLite.
        """
        if hasattr(self.db, "connection"):
            return self.db.connection.cursor()
        else:
            import sqlite3
            conn = sqlite3.connect(self.db)
            return conn.cursor()

    def _execute_and_commit(self, query, params=None):
        """
        Ejecuta una consulta SQL y realiza commit si es posible.
        :param query: Consulta SQL a ejecutar.
        :param params: Parámetros para la consulta.
        :return: True si la ejecución es exitosa, False si falla.
        """
        try:
            self.cursor.execute(query, params or ())
            if hasattr(self.db, "commit") and callable(self.db.commit):
                self.db.commit()
            elif hasattr(self.db, "connection") and hasattr(self.db.connection, "commit") and callable(self.db.connection.commit):
                self.db.connection.commit()
            return True
        except sqlite3.Error as e:
            traceback.print_exc()
            return False

    def get_student_by_identification(self, identificacion):
        """
        Obtiene un estudiante por su identificación.
        :param identificacion: Identificación del estudiante.
        :return: Registro del estudiante como sqlite3.Row o None.
        """
        try:
            query = "SELECT * FROM estudiantes WHERE identificacion = ?"
            self.cursor.execute(query, (identificacion,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            traceback.print_exc()
            return None

    def get_student_by_id(self, student_id):
        """
        Obtiene un estudiante por su ID.
        :param student_id: ID del estudiante.
        :return: Registro del estudiante como diccionario o None.
        """
        try:
            query = "SELECT * FROM estudiantes WHERE id = ?"
            self.cursor.execute(query, (student_id,))
            row = self.cursor.fetchone()
            if row:
                return dict(row)
            return None
        except Exception as e:
            detailed_error = traceback.format_exc()
            print(f"Error al obtener el estudiante con ID {student_id}: {e}\nDetalle:\n{detailed_error}")
            return None

    def get_course_name(self, course_id):
        """
        Obtiene el nombre completo del curso basado en el course_id.
        Ahora incluye la sección si existe (por ejemplo, "Tercero - A").
        :param course_id: ID del curso.
        :return: Nombre del curso o "N/A" si no se encuentra.
        """
        if course_id is None:
            return "N/A"
        try:
            self.cursor.execute("SELECT name, seccion FROM courses WHERE id = ?", (course_id,))
            result = self.cursor.fetchone()
            if result:
                name = result[0]
                seccion = result[1] if len(result) > 1 and result[1] else ""
                return f"{name} - {seccion}" if seccion.strip() else name
            return "N/A"
        except sqlite3.Error as e:
            traceback.print_exc()
            return "N/A"

    def get_all_students(self):
        """
        Obtiene todos los estudiantes con información del curso.
        :return: Lista de diccionarios con datos de los estudiantes.
        """
        try:
            query = "SELECT id, identificacion, nombre, apellido, course_id, representante, telefono, active FROM estudiantes"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
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
            traceback.print_exc()
            return []

    def delete_student(self, identificacion):
        """
        Elimina un estudiante basado en su identificación.
        :param identificacion: Identificación del estudiante.
        :return: Tupla (éxito: bool, mensaje: str).
        """
        if not self.get_student_by_identification(identificacion):
            return False, "Estudiante no encontrado."
        if self._execute_and_commit("DELETE FROM estudiantes WHERE identificacion = ?", (identificacion,)):
            return True, "Estudiante eliminado correctamente."
        return False, "Error al eliminar el estudiante."

    def deactivate_student(self, identificacion):
        """
        Desactiva un estudiante basado en su identificación.
        :param identificacion: Identificación del estudiante.
        :return: Tupla (éxito: bool, mensaje: str).
        """
        if not self.get_student_by_identification(identificacion):
            return False, "Estudiante no encontrado."
        if self._execute_and_commit("UPDATE estudiantes SET active = 0 WHERE identificacion = ?", (identificacion,)):
            return True, "Estudiante desactivado correctamente."
        return False, "Error al desactivar el estudiante."

    def register_student(self, identificacion, nombre, apellido, course_id, representante, telefono):
        """
        Registra un nuevo estudiante en la base de datos.
        Verifica que el número de identificación sea numérico.
        :return: Tupla (éxito: bool, mensaje: str).
        """
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
        if self._execute_and_commit(query, (identificacion, nombre, apellido, course_id, representante, telefono)):
            return True, "Estudiante registrado correctamente."
        return False, "Error al registrar el estudiante."

    def get_payments_by_student(self, student_identificacion):
        """
        Retorna una lista de pagos asociados al estudiante.
        Cada pago se devuelve como un diccionario con la clave "amount".
        :param student_identificacion: Identificación del estudiante.
        :return: Lista de diccionarios con los pagos.
        """
        try:
            self.cursor.execute("SELECT id FROM estudiantes WHERE identificacion = ?", (student_identificacion,))
            student_record = self.cursor.fetchone()
            if not student_record:
                return []
            
            student_id = student_record[0]
            self.cursor.execute("SELECT monto FROM pagos WHERE estudiante_id = ?", (student_id,))
            return [{"amount": row[0]} for row in self.cursor.fetchall()] if self.cursor.rowcount > 0 else []
        except sqlite3.Error as e:
            traceback.print_exc()
            return []

    def update_student_course(self, student_id, new_course_id):
        """
        Actualiza el course_id de un estudiante en la tabla estudiantes.
        :param student_id: ID del estudiante.
        :param new_course_id: Nuevo course_id a asignar.
        :return: Tupla (éxito: bool, mensaje: str).
        """
        try:
            if self._execute_and_commit("UPDATE estudiantes SET course_id = ? WHERE id = ?", (new_course_id, student_id)):
                return True, "Curso actualizado correctamente."
            return False, "Error al actualizar el curso."
        except sqlite3.Error as e:
            traceback.print_exc()
            return False, f"Error al actualizar el curso: {e}"
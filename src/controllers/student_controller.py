import sqlite3
import traceback

class StudentController:
    def __init__(self, db):
        self.db = db

    def _get_cursor(self):
        """
        Método auxiliar para obtener un cursor válido.
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

    def _execute_and_commit(self, query, params=None):
        """
        Ejecuta una consulta SQL y realiza commit si es posible.
        """
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
        """
        Obtiene un estudiante por su identificación.
        """
        cursor = self._get_cursor()
        query = "SELECT * FROM estudiantes WHERE identificacion = ?"
        cursor.execute(query, (identificacion,))
        return cursor.fetchone()

    def get_course_name(self, course_id):
        """
        Obtiene el nombre del curso basado en el course_id.
        """
        if course_id is None:
            return "N/A"
        cursor = self._get_cursor()
        cursor.execute("SELECT name FROM courses WHERE id = ?", (course_id,))
        result = cursor.fetchone()
        return result[0] if result else "N/A"

    def get_all_students(self):
        """
        Obtiene todos los estudiantes con información del curso.
        """
        cursor = self._get_cursor()
        cursor.execute("SELECT id, identificacion, nombre, apellido, course_id, representante, telefono, active FROM estudiantes")
        rows = cursor.fetchall()
        students = []
        for row in rows:
            course_name = self.get_course_name(row[4]) if row[4] else "N/A"
            students.append({
                "id": row[0],
                "identificacion": row[1],
                "nombre": row[2],
                "apellido": row[3],
                "course_name": course_name,
                "representante": row[5],
                "telefono": row[6],
                "active": row[7]
            })
        return students

    def delete_student(self, identificacion):
        """
        Elimina un estudiante basado en su identificación.
        """
        if not self.get_student_by_identification(identificacion):
            return False, "Estudiante no encontrado."
        query = "DELETE FROM estudiantes WHERE identificacion = ?"
        if self._execute_and_commit(query, (identificacion,)):
            return True, "Estudiante eliminado correctamente."
        return False, "Error al eliminar el estudiante."

    def deactivate_student(self, identificacion):
        """
        Desactiva un estudiante basado en su identificación.
        """
        if not self.get_student_by_identification(identificacion):
            return False, "Estudiante no encontrado."
        query = "UPDATE estudiantes SET active = 0 WHERE identificacion = ?"
        if self._execute_and_commit(query, (identificacion,)):
            return True, "Estudiante desactivado correctamente."
        return False, "Error al desactivar el estudiante."

    def register_student(self, identificacion, nombre, apellido, course_id, representante, telefono):
        """
        Registra un nuevo estudiante en la base de datos.
        """
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
        """
        try:
            # Obtener el id del estudiante usando su identificación
            query_student = "SELECT id FROM estudiantes WHERE identificacion = ?"
            cursor = self._get_cursor()
            cursor.execute(query_student, (student_identificacion,))
            student_record = cursor.fetchone()
            if not student_record:
                return []

            student_id = student_record[0]

            # Consultar los pagos asociados al id del estudiante
            query_payments = "SELECT monto FROM pagos WHERE estudiante_id = ?"
            cursor.execute(query_payments, (student_id,))
            results = cursor.fetchall()
            payments = [{"amount": row[0]} for row in results]
            return payments

        except Exception as e:
            print(f"Error al obtener pagos del estudiante: {e}")
            return []

    def get_all_configs(self):
        """
        Obtiene todas las configuraciones desde la tabla config.
        Nota: Este método podría ser movido a un ConfigController.
        """
        try:
            cursor = self._get_cursor()
            query = "SELECT key, value FROM config"
            cursor.execute(query)
            rows = cursor.fetchall()
            return {key: value for key, value in rows}
        except Exception:
            traceback.print_exc()
            return {
                "SCHOOL_NAME": "Nombre del Colegio",
                "LOGO_PATH": "D:\\laragon\\www\\colegio_app\\assets\\logo.png"
            }
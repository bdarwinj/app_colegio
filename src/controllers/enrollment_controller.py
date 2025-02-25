import sqlite3
import datetime
import traceback

class EnrollmentController:
    def __init__(self, db):
        self.db = db

    def _get_cursor(self):
        if hasattr(self.db, "cursor") and callable(self.db.cursor):
            return self.db.cursor()
        elif hasattr(self.db, "connection") and hasattr(self.db.connection, "cursor") and callable(self.db.connection.cursor):
            return self.db.connection.cursor()
        else:
            raise AttributeError("El objeto de base de datos no tiene un método 'cursor'.")

    def _commit(self):
        if hasattr(self.db, "commit") and callable(self.db.commit):
            self.db.commit()
        elif hasattr(self.db, "connection") and hasattr(self.db.connection, "commit") and callable(self.db.connection.commit):
            self.db.connection.commit()
        else:
            print("Advertencia: No se encontró método commit.")

    def create_enrollment(self, student_id, course_id, academic_year, status="inscrito"):
        """
        Crea una nueva inscripción para un estudiante en un año académico determinado.
        :param student_id: ID del estudiante.
        :param course_id: ID del curso (grado y sección) en el que se inscribe.
        :param academic_year: Año académico (por ejemplo, 2025).
        :param status: Estado inicial (por defecto "inscrito").
        :return: Tupla (éxito: bool, mensaje: str, enrollment_id: int o None)
        """
        try:
            date_enrolled = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            query = """
                INSERT INTO enrollments (student_id, course_id, academic_year, status, date_enrolled)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor = self._get_cursor()
            cursor.execute(query, (student_id, course_id, academic_year, status, date_enrolled))
            self._commit()
            return True, "Inscripción creada correctamente.", cursor.lastrowid
        except sqlite3.Error as e:
            traceback.print_exc()
            return False, f"Error al crear inscripción: {e}", None

    def update_enrollment_status(self, enrollment_id, new_status):
        """
        Actualiza el estado de una inscripción.
        :param enrollment_id: ID de la inscripción.
        :param new_status: Nuevo estado (por ejemplo, "promovido", "repetido").
        :return: Tupla (éxito: bool, mensaje: str)
        """
        try:
            query = "UPDATE enrollments SET status = ? WHERE id = ?"
            cursor = self._get_cursor()
            cursor.execute(query, (new_status, enrollment_id))
            self._commit()
            return True, "Inscripción actualizada correctamente."
        except sqlite3.Error as e:
            traceback.print_exc()
            return False, f"Error al actualizar la inscripción: {e}"

    def get_all_enrollments(self):
        """
        Recupera todas las inscripciones ordenadas por año académico descendente.
        :return: Lista de diccionarios con los datos de las inscripciones.
        """
        try:
            query = "SELECT * FROM enrollments ORDER BY academic_year DESC"
            cursor = self._get_cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            traceback.print_exc()
            return []

    def get_enrollment_history(self, student_id):
        """
        Recupera el historial completo de inscripciones de un estudiante.
        :param student_id: ID del estudiante.
        :return: Lista de inscripciones (diccionarios) ordenadas por año académico descendente.
        """
        try:
            query = "SELECT * FROM enrollments WHERE student_id = ? ORDER BY academic_year DESC"
            cursor = self._get_cursor()
            cursor.execute(query, (student_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            traceback.print_exc()
            return []

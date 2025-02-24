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
        Recupera todas las inscripciones sin filtrar, ordenadas por año académico descendente.
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

    # Si ya tenías otro método, puedes mantenerlo y agregar este para obtener todos los registros.
    def get_enrollments_by_student(self, student_id):
        """
        Recupera todas las inscripciones para un estudiante específico.
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
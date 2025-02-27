import sqlite3
import datetime
import traceback
from src.utils.progression import get_next_course

class EnrollmentController:
    def __init__(self, db, student_controller, course_controller):
        """
        Inicializa el controlador de inscripciones.
        :param db: Instancia de Database o ruta a la base de datos.
        :param student_controller: Controlador para manejar estudiantes.
        :param course_controller: Controlador para manejar cursos.
        """
        self.db = db
        self.student_controller = student_controller
        self.course_controller = course_controller
        self.cursor = self._get_cursor()

    def _get_cursor(self):
        """
        Obtiene un cursor persistente para la base de datos.
        :return: Cursor de la conexión SQLite.
        """
        if hasattr(self.db, "connection"):
            return self.db.connection.cursor()
        else:
            conn = sqlite3.connect(self.db)
            return conn.cursor()

    def _execute_and_commit(self, query, params=()):
        """
        Ejecuta una consulta y confirma los cambios.
        :param query: Consulta SQL a ejecutar.
        :param params: Parámetros para la consulta.
        :return: True si la ejecución es exitosa, False si falla.
        """
        try:
            self.cursor.execute(query, params)
            if hasattr(self.db, "connection"):
                self.db.connection.commit()
            return True
        except sqlite3.Error as e:
            traceback.print_exc()
            return False

    def get_enrollment_by_id(self, enrollment_id):
        """Obtiene una inscripción por su ID."""
        try:
            query = "SELECT * FROM enrollments WHERE id = ?"
            self.cursor.execute(query, (enrollment_id,))
            result = self.cursor.fetchone()
            return dict(result) if result else None
        except sqlite3.Error as e:
            traceback.print_exc()
            return None

    def update_enrollment_status(self, enrollment_id, status):
        """Actualiza el estado de una inscripción."""
        if not status or not isinstance(status, str):
            return False, "El estado debe ser una cadena no vacía."
        try:
            query = "UPDATE enrollments SET status = ? WHERE id = ?"
            if self._execute_and_commit(query, (status, enrollment_id)):
                return True, "Estado actualizado correctamente."
            return False, "Error al actualizar el estado."
        except Exception as e:
            traceback.print_exc()
            return False, f"Error al actualizar el estado: {e}"

    def create_enrollment(self, student_id, course_id, academic_year, status="inscrito"):
        """Crea una nueva inscripción e inserta la fecha de inscripción."""
        if not isinstance(academic_year, int) or academic_year < 0:
            return False, "El año académico debe ser un número entero positivo."
        try:
            date_enrolled = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            query = """
                INSERT INTO enrollments (student_id, course_id, academic_year, status, date_enrolled)
                VALUES (?, ?, ?, ?, ?)
            """
            if self._execute_and_commit(query, (student_id, course_id, academic_year, status, date_enrolled)):
                new_id = self.cursor.lastrowid
                return True, "Inscripción creada correctamente.", new_id
            return False, "Error al crear inscripción.", None
        except Exception as e:
            traceback.print_exc()
            return False, f"Error al crear inscripción: {e}", None

    def promote_student(self, enrollment_id):
        """
        Promueve al estudiante al siguiente curso y crea una nueva inscripción para el próximo año académico.
        :param enrollment_id: ID de la inscripción actual.
        :return: Tupla (éxito: bool, mensaje: str)
        """
        try:
            enrollment = self.get_enrollment_by_id(enrollment_id)
            if not enrollment:
                return False, "Inscripción no encontrada."
            
            student_id = enrollment["student_id"]
            current_course_id = enrollment["course_id"]
            current_course = self.course_controller.get_course_by_id(current_course_id)
            if not current_course:
                return False, "Curso actual no encontrado."
            current_grade = current_course["name"]
            
            next_grade = get_next_course(current_grade)
            if next_grade == current_grade:
                return False, "El estudiante ya está en el último curso."
            
            next_courses = self.course_controller.get_courses_by_grade(next_grade)
            if not next_courses:
                return False, f"No hay cursos disponibles para el grado {next_grade}."
            next_course_id = next_courses[0]["id"]
            
            success, msg = self.student_controller.update_student_course(student_id, next_course_id)
            if not success:
                return False, msg
            
            next_year = enrollment["academic_year"] + 1
            enroll_success, enroll_msg, new_enrollment_id = self.create_enrollment(
                student_id, next_course_id, next_year, status="inscrito"
            )
            if enroll_success:
                return True, "Estudiante promovido y nueva inscripción creada."
            return False, enroll_msg
        except Exception as e:
            traceback.print_exc()
            return False, f"Error al promover al estudiante: {e}"

    def get_all_enrollments(self):
        """
        Recupera todas las inscripciones ordenadas por año académico descendente.
        :return: Lista de diccionarios con los datos de las inscripciones.
        """
        try:
            query = "SELECT * FROM enrollments ORDER BY academic_year DESC"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows] if rows else []
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
            self.cursor.execute(query, (student_id,))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows] if rows else []
        except sqlite3.Error as e:
            traceback.print_exc()
            return []
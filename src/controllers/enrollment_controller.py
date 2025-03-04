# src/controllers/enrollment_controller.py
import sqlite3
import datetime
from src.utils.db_utils import db_cursor
from src.utils.progression import get_next_course
from src.logger import logger

class EnrollmentController:
    def __init__(self, db, student_controller, course_controller):
        """
        Inicializa el controlador de inscripciones.
        :param db: Instancia de Database o conexión a la base de datos.
        :param student_controller: Controlador para manejar estudiantes.
        :param course_controller: Controlador para manejar cursos.
        """
        self.db = db
        self.student_controller = student_controller
        self.course_controller = course_controller

    def get_enrollment_by_id(self, enrollment_id):
        try:
            query = "SELECT * FROM enrollments WHERE id = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (enrollment_id,))
                result = cursor.fetchone()
            return dict(result) if result else None
        except sqlite3.Error as e:
            logger.exception("Error en get_enrollment_by_id")
            return None

    def update_enrollment_status(self, enrollment_id, status):
        if not status or not isinstance(status, str):
            return False, "El estado debe ser una cadena no vacía."
        try:
            query = "UPDATE enrollments SET status = ? WHERE id = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (status, enrollment_id))
            return True, "Estado actualizado correctamente."
        except Exception as e:
            logger.exception("Error al actualizar el estado de la inscripción")
            return False, f"Error al actualizar el estado: {e}"

    def create_enrollment(self, student_id, course_id, academic_year, status="inscrito"):
        if not isinstance(academic_year, int) or academic_year < 0:
            return False, "El año académico debe ser un número entero positivo.", None
        try:
            date_enrolled = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            query = """
                INSERT INTO enrollments (student_id, course_id, academic_year, status, date_enrolled)
                VALUES (?, ?, ?, ?, ?)
            """
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (student_id, course_id, academic_year, status, date_enrolled))
                new_id = cursor.lastrowid
            return True, "Inscripción creada correctamente.", new_id
        except Exception as e:
            logger.exception("Error al crear inscripción")
            return False, f"Error al crear inscripción: {e}", None

    def promote_student(self, enrollment_id):
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
            logger.exception("Error al promover al estudiante")
            return False, f"Error al promover al estudiante: {e}"

    def get_all_enrollments(self):
        try:
            query = "SELECT * FROM enrollments ORDER BY academic_year DESC"
            with db_cursor(self.db) as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
            return [dict(row) for row in rows] if rows else []
        except sqlite3.Error as e:
            logger.exception("Error al obtener todas las inscripciones")
            return []

    def get_enrollment_history(self, student_id):
        try:
            query = "SELECT * FROM enrollments WHERE student_id = ? ORDER BY academic_year DESC"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (student_id,))
                rows = cursor.fetchall()
            return [dict(row) for row in rows] if rows else []
        except sqlite3.Error as e:
            logger.exception("Error al obtener el historial de inscripciones")
            return []

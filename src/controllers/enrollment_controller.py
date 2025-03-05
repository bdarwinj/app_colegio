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

    def _execute_fetchone(self, query, params, error_context, default_return=None):
        """
        Ejecuta una consulta que retorna una sola fila.
        """
        try:
            with db_cursor(self.db) as cursor:
                cursor.execute(query, params)
                row = cursor.fetchone()
            return dict(row) if row else default_return
        except sqlite3.Error as e:
            logger.exception(error_context)
            return default_return

    def _execute_fetchall(self, query, params, error_context, default_return=[]):
        """
        Ejecuta una consulta que retorna varias filas.
        """
        try:
            with db_cursor(self.db) as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
            return [dict(row) for row in rows] if rows else default_return
        except sqlite3.Error as e:
            logger.exception(error_context)
            return default_return

    def _execute_update(self, query, params, success_message, error_context, error_prefix="Error: "):
        """
        Ejecuta una consulta de actualización o eliminación.
        """
        try:
            with db_cursor(self.db) as cursor:
                cursor.execute(query, params)
            return True, success_message
        except Exception as e:
            logger.exception(error_context)
            return False, f"{error_prefix}{e}"

    def _execute_insert(self, query, params, success_message, error_context, error_prefix="Error: "):
        """
        Ejecuta una consulta de inserción y retorna el ID de la nueva fila.
        """
        try:
            with db_cursor(self.db) as cursor:
                cursor.execute(query, params)
                new_id = cursor.lastrowid
            return True, success_message, new_id
        except Exception as e:
            logger.exception(error_context)
            return False, f"{error_prefix}{e}", None

    def get_enrollment_by_id(self, enrollment_id):
        query = "SELECT * FROM enrollments WHERE id = ?"
        return self._execute_fetchone(query, (enrollment_id,), "Error en get_enrollment_by_id", None)

    def update_enrollment_status(self, enrollment_id, status):
        if not status or not isinstance(status, str):
            return False, "El estado debe ser una cadena no vacía."
        query = "UPDATE enrollments SET status = ? WHERE id = ?"
        return self._execute_update(
            query,
            (status, enrollment_id),
            "Estado actualizado correctamente.",
            "Error al actualizar el estado de la inscripción",
            "Error al actualizar el estado: "
        )

    def create_enrollment(self, student_id, course_id, academic_year, status="inscrito"):
        if not isinstance(academic_year, int) or academic_year < 0:
            return False, "El año académico debe ser un número entero positivo.", None
        date_enrolled = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = """
                INSERT INTO enrollments (student_id, course_id, academic_year, status, date_enrolled)
                VALUES (?, ?, ?, ?, ?)
            """
        return self._execute_insert(
            query,
            (student_id, course_id, academic_year, status, date_enrolled),
            "Inscripción creada correctamente.",
            "Error al crear inscripción",
            "Error al crear inscripción: "
        )

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
        query = "SELECT * FROM enrollments ORDER BY academic_year DESC"
        return self._execute_fetchall(query, (), "Error al obtener todas las inscripciones", [])

    def get_enrollment_history(self, student_id):
        query = "SELECT * FROM enrollments WHERE student_id = ? ORDER BY academic_year DESC"
        return self._execute_fetchall(query, (student_id,), "Error al obtener el historial de inscripciones", [])

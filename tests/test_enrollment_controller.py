# tests/test_enrollment_controller.py
import os
import sqlite3
import unittest
import datetime
from src.models.database import Database
from src.controllers.student_controller import StudentController
from src.controllers.course_controller import CourseController
from src.controllers.enrollment_controller import EnrollmentController

class TestEnrollmentController(unittest.TestCase):
    def setUp(self):
        self.temp_db = "test_temp.db"
        self.database = Database(self.temp_db)
        self.database.create_tables()
        self.student_controller = StudentController(self.database)
        self.course_controller = CourseController(self.database)
        self.enrollment_controller = EnrollmentController(self.database, self.student_controller, self.course_controller)
        # Insertar cursos para "primero" y "segundo"
        self.course_controller.add_course("primero", "A")
        self.course_controller.add_course("segundo", "A")
        # Registrar un estudiante y una inscripción para "primero"
        self.student_controller.register_student("11111", "Alice", "Smith", 1, "Bob Smith", "555-1111")
        student = self.student_controller.get_student_by_identification("11111")
        self.student_id = student["id"]
        current_year = datetime.datetime.now().year
        success, msg, enrollment_id = self.enrollment_controller.create_enrollment(self.student_id, 1, current_year, status="inscrito")
        self.enrollment_id = enrollment_id

    def tearDown(self):
        self.database.close()
        if os.path.exists(self.temp_db):
            os.remove(self.temp_db)

    def test_promotion(self):
        # Promover al estudiante: de "primero" a "segundo"
        success, msg = self.enrollment_controller.promote_student(self.enrollment_id)
        self.assertTrue(success, msg)
        # Verificar que el curso del estudiante se haya actualizado a "segundo" (id=2)
        student = self.student_controller.get_student_by_id(self.student_id)
        self.assertEqual(student["course_id"], 2)
        # Verificar que se creó una nueva inscripción para el próximo año
        enrollments = self.enrollment_controller.get_enrollment_history(self.student_id)
        expected_year = datetime.datetime.now().year + 1
        self.assertTrue(any(enr["academic_year"] == expected_year for enr in enrollments))

if __name__ == '__main__':
    unittest.main()

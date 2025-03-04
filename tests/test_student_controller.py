# tests/test_student_controller.py
import os
import sqlite3
import unittest
from src.models.database import Database
from src.controllers.student_controller import StudentController

class TestStudentController(unittest.TestCase):
    def setUp(self):
        # Crear una base de datos temporal para pruebas
        self.temp_db = "test_temp.db"
        self.database = Database(self.temp_db)
        self.database.create_tables()
        self.student_controller = StudentController(self.database)

    def tearDown(self):
        self.database.close()
        if os.path.exists(self.temp_db):
            os.remove(self.temp_db)

    def test_register_and_get_student(self):
        success, msg = self.student_controller.register_student("12345", "John", "Doe", 1, "Jane Doe", "555-1234")
        self.assertTrue(success, msg)
        student = self.student_controller.get_student_by_identification("12345")
        self.assertIsNotNone(student)
        self.assertEqual(student["nombre"], "John")
        self.assertEqual(student["apellido"], "Doe")

if __name__ == '__main__':
    unittest.main()

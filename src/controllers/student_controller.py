from src.models.student import Student

class StudentController:
    def __init__(self, db):
        self.db = db

    def register_student(self, identificacion, nombre, apellido, course_id, representante, telefono):
        try:
            query = '''
                INSERT INTO estudiantes (identificacion, nombre, apellido, course_id, representante, telefono)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            self.db.cursor.execute(query, (identificacion, nombre, apellido, course_id, representante, telefono))
            self.db.connection.commit()
            return True, "Estudiante registrado correctamente."
        except Exception as e:
            return False, f"Error: {e}"

    def get_all_students(self):
        query = '''SELECT e.*, c.name as course_name FROM estudiantes e
                   LEFT JOIN courses c ON e.course_id = c.id'''
        self.db.cursor.execute(query)
        return self.db.cursor.fetchall()
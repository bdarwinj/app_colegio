from src.models.course import Course

class CourseController:
    def __init__(self, db):
        self.db = db

    def add_course(self, name):
        try:
            query = "INSERT INTO courses (name, active) VALUES (?, 1)"
            self.db.cursor.execute(query, (name,))
            self.db.connection.commit()
            return True, "Curso agregado correctamente."
        except Exception as e:
            return False, f"Error al agregar curso: {e}"

    def edit_course(self, course_id, new_name):
        try:
            query = "UPDATE courses SET name = ? WHERE id = ?"
            self.db.cursor.execute(query, (new_name, course_id))
            self.db.connection.commit()
            return True, "Curso editado correctamente."
        except Exception as e:
            return False, f"Error al editar curso: {e}"

    def deactivate_course(self, course_id):
        try:
            query = "UPDATE courses SET active = 0 WHERE id = ?"
            self.db.cursor.execute(query, (course_id,))
            self.db.connection.commit()
            return True, "Curso desactivado correctamente."
        except Exception as e:
            return False, f"Error al desactivar curso: {e}"

    def get_active_courses(self):
        query = "SELECT * FROM courses WHERE active = 1"
        self.db.cursor.execute(query)
        courses = self.db.cursor.fetchall()
        return courses

    def get_all_courses(self):
        query = "SELECT * FROM courses"
        self.db.cursor.execute(query)
        courses = self.db.cursor.fetchall()
        return courses
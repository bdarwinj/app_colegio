class Course:
    def __init__(self, course_id, name, active=True):
        self.id = course_id
        self.name = name
        self.active = active

    def __repr__(self):
        return f"{self.name} ({'Activo' if self.active else 'Desactivado'})"
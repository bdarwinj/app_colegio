class Student:
    def __init__(self, identificacion, nombre, apellido, course_id, representante, telefono):
        self.identificacion = identificacion
        self.nombre = nombre
        self.apellido = apellido
        self.course_id = course_id
        self.representante = representante
        self.telefono = telefono

    def __repr__(self):
        return f'{self.nombre} {self.apellido}'
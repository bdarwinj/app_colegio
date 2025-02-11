import sqlite3

class Database:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row  # Acceso a columnas por nombre
        self.cursor = self.connection.cursor()

    def create_tables(self):
        # Tabla de Usuarios
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT
            )
        ''')
        # Tabla de Estudiantes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS estudiantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identificacion TEXT UNIQUE,
                nombre TEXT,
                apellido TEXT,
                course_id INTEGER,
                representante TEXT,
                telefono TEXT,
                FOREIGN KEY(course_id) REFERENCES courses(id)
            )
        ''')
        # Tabla de Pagos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estudiante_id INTEGER,
                fecha TEXT,
                monto REAL,
                responsable TEXT,
                FOREIGN KEY(estudiante_id) REFERENCES estudiantes(id)
            )
        ''')
        # Tabla de Cursos (Grados)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                active INTEGER DEFAULT 1
            )
        ''')
        # Tabla de Configuración
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        self.connection.commit()

    def close(self):
        self.connection.close()
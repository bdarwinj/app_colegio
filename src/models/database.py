# src/models/database.py
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
                active INTEGER DEFAULT 1,
                FOREIGN KEY(course_id) REFERENCES courses(id)
            )
        ''')
        # Verificar si la columna 'active' existe y añadirla si no
        self.cursor.execute("PRAGMA table_info(estudiantes)")
        columns = [col[1] for col in self.cursor.fetchall()]
        if 'active' not in columns:
            self.cursor.execute("ALTER TABLE estudiantes ADD COLUMN active INTEGER DEFAULT 1")
        self.connection.commit()
        
        # Tabla de Pagos (Unificación de nomenclatura: se usa "payments")
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                enrollment_id INTEGER,
                amount REAL,
                description TEXT,
                payment_date TEXT,
                receipt_number TEXT,
                FOREIGN KEY(enrollment_id) REFERENCES enrollments(id)
            )
        ''')
        
        # Tabla de Cursos (Grados) con columna "seccion"
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                seccion TEXT,
                active INTEGER DEFAULT 1,
                UNIQUE(name, seccion)
            )
        ''')
        
        # Tabla de Configuración
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Tabla de Inscripciones (Enrollments)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                course_id INTEGER,
                academic_year INTEGER,
                status TEXT,
                date_enrolled TEXT,
                FOREIGN KEY(student_id) REFERENCES estudiantes(id),
                FOREIGN KEY(course_id) REFERENCES courses(id)
            )
        ''')
        
        self.connection.commit()

    def close(self):
        self.connection.close()

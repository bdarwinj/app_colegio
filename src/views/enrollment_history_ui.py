import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from src.controllers.enrollment_controller import EnrollmentController
from src.controllers.course_controller import CourseController

class EnrollmentHistoryUI(tk.Toplevel):
    def __init__(self, root, db, student_controller, course_controller, student_id):
        super().__init__(root)
        self.db = db
        self.student_controller = student_controller
        self.course_controller = course_controller
        self.student_id = student_id
        
        # Instanciar EnrollmentController
        self.enrollment_controller = EnrollmentController(self.db, self.student_controller, self.course_controller)
        
        self.title(f"Historial de Inscripciones - Estudiante {student_id}")
        self.geometry("700x500")
        
        self.create_widgets()
        self.load_history()

    def create_widgets(self):
        """Crea y configura el Treeview para mostrar el historial de inscripciones."""
        columns = ("id", "course", "academic_year", "status", "date_enrolled")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        headers = {
            "id": "ID",
            "course": "Curso",
            "academic_year": "Año Académico",
            "status": "Estado",
            "date_enrolled": "Fecha de Inscripción"
        }
        col_widths = {"id": 50, "course": 180, "academic_year": 100, "status": 100, "date_enrolled": 150}
        
        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=col_widths[col], anchor="center")
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def clear_treeview(self):
        """Elimina todos los elementos del Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def load_history(self):
        """Carga el historial de inscripciones del estudiante y lo muestra en la tabla."""
        try:
            history = self.enrollment_controller.get_enrollment_history(self.student_id)
            self.clear_treeview()

            course_cache = {}  # Cache para evitar múltiples consultas a la BD

            for enr in history:
                course_id = enr.get("course_id", "N/A")
                
                if course_id not in course_cache and course_id != "N/A":
                    course_data = self.course_controller.get_course_by_id(course_id)
                    if course_data:
                        name = course_data.get("name", "")
                        seccion = course_data.get("seccion", "")
                        course_cache[course_id] = f"{name} - {seccion}" if seccion.strip() else name
                    else:
                        course_cache[course_id] = "N/A"
                
                course_display = course_cache.get(course_id, "N/A")
                
                self.tree.insert("", "end", values=(
                    enr.get("id", "N/A"),
                    course_display,
                    enr.get("academic_year", "N/A"),
                    enr.get("status", "N/A"),
                    enr.get("date_enrolled", "N/A")
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el historial: {e}")
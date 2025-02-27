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
        # Instanciar EnrollmentController con los tres parámetros requeridos
        self.enrollment_controller = EnrollmentController(self.db, self.student_controller, self.course_controller)
        self.title(f"Historial de Inscripciones - Estudiante {student_id}")
        self.geometry("700x500")
        self.create_widgets()
        self.load_history()

    def create_widgets(self):
        self.tree = ttk.Treeview(
            self,
            columns=("id", "course", "academic_year", "status", "date_enrolled"),
            show="headings"
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("course", text="Curso")
        self.tree.heading("academic_year", text="Año Académico")
        self.tree.heading("status", text="Estado")
        self.tree.heading("date_enrolled", text="Fecha de Inscripción")
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("course", width=150, anchor="center")
        self.tree.column("academic_year", width=100, anchor="center")
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("date_enrolled", width=150, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def load_history(self):
        try:
            history = self.enrollment_controller.get_enrollment_history(self.student_id)
            # Limpiar el Treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            # Insertar cada inscripción
            for enr in history:
                course_id = enr.get("course_id")
                if course_id:
                    course_data = self.course_controller.get_course_by_id(course_id)
                    if course_data:
                        name = course_data.get("name", "")
                        seccion = course_data.get("seccion", "")
                        course_display = f"{name} - {seccion}" if seccion and seccion.strip() else name
                    else:
                        course_display = "N/A"
                else:
                    course_display = "N/A"
                self.tree.insert("", "end", values=(
                    enr.get("id"),
                    course_display,
                    enr.get("academic_year"),
                    enr.get("status"),
                    enr.get("date_enrolled")
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el historial: {e}")

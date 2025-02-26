import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from src.controllers.enrollment_controller import EnrollmentController
from src.controllers.course_controller import CourseController

class EnrollmentManagementUI:
    def __init__(self, db):
        """
        Inicializa la interfaz de gestión de inscripciones.
        :param db: Objeto de conexión a la base de datos.
        """
        self.db = db
        self.enrollment_controller = EnrollmentController(db)
        self.course_controller = CourseController(db)  # Para obtener el nombre del curso
        self.window = tk.Toplevel()
        self.window.title("Gestión de Inscripciones")
        self.window.geometry("700x500")
        self.create_widgets()
        self.load_enrollments()

    def create_widgets(self):
        # Treeview para mostrar las inscripciones del año actual
        self.tree = ttk.Treeview(self.window, columns=("id", "student_id", "course", "academic_year", "status"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("student_id", text="Estudiante")
        self.tree.heading("course", text="Curso")
        self.tree.heading("academic_year", text="Año Académico")
        self.tree.heading("status", text="Estado")
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("student_id", width=100, anchor="center")
        self.tree.column("course", width=150, anchor="center")
        self.tree.column("academic_year", width=100, anchor="center")
        self.tree.column("status", width=100, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Vincular doble clic para ver historial completo de inscripciones
        self.tree.bind("<Double-1>", self.on_row_double_click)
        
        # Frame para actualizar el estado de la inscripción seleccionada.
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(pady=10)
        ttk.Label(btn_frame, text="Nuevo Estado:").pack(side="left", padx=5)
        self.status_var = tk.StringVar(value="promovido")
        self.combo_status = ttk.Combobox(btn_frame, textvariable=self.status_var, state="readonly", values=["promovido", "repetido"])
        self.combo_status.pack(side="left", padx=5)
        btn_update = ttk.Button(btn_frame, text="Procesar Inscripción", command=self.process_enrollment)
        btn_update.pack(side="left", padx=5)

    def load_enrollments(self):
        """
        Carga en el Treeview las inscripciones correspondientes al año académico actual.
        Se obtiene todo el historial y se filtra por el año actual.
        Para cada inscripción, se consulta el curso para mostrar su nombre.
        """
        all_enrollments = self.enrollment_controller.get_all_enrollments()
        current_year = datetime.datetime.now().year
        enrollments = [enr for enr in all_enrollments if enr.get("academic_year") == current_year]
        
        # Limpiar el Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Insertar cada inscripción en el Treeview
        for enrollment in enrollments:
            course_id = enrollment.get("course_id")
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
                enrollment["id"],
                enrollment["student_id"],
                course_display,
                enrollment["academic_year"],
                enrollment["status"]
            ))

    def on_row_double_click(self, event):
        """
        Al hacer doble clic en una inscripción, abre una ventana que muestra el historial completo de inscripciones del estudiante.
        """
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        student_id = item["values"][1]  # La segunda columna es el ID del estudiante
        from src.views.enrollment_history_ui import EnrollmentHistoryUI
        EnrollmentHistoryUI(self.db, student_id)

    def process_enrollment(self):
        """
        Permite al administrador actualizar el estado de la inscripción seleccionada.
        Por ejemplo, si el estudiante fue evaluado y se decide que pasó (promovido) o debe repetir.
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección requerida", "Por favor, seleccione una inscripción para procesar.")
            return
        
        enrollment_item = self.tree.item(selected[0])
        enrollment_id = enrollment_item["values"][0]
        new_status = self.status_var.get()
        success, msg = self.enrollment_controller.update_enrollment_status(enrollment_id, new_status)
        if success:
            messagebox.showinfo("Éxito", "Inscripción actualizada correctamente.")
            # Aquí se podría crear una nueva inscripción para el siguiente año, si se requiere.
            self.load_enrollments()
        else:
            messagebox.showerror("Error", msg)

if __name__ == "__main__":
    import sqlite3
    db = sqlite3.connect("colegio.db")
    db.row_factory = sqlite3.Row
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    ui = EnrollmentManagementUI(db)
    root.mainloop()

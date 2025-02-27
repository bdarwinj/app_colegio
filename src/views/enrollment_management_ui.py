import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from src.controllers.enrollment_controller import EnrollmentController
from src.controllers.course_controller import CourseController
from src.controllers.student_controller import StudentController
from src.utils.progression import get_next_course
from src.views.enrollment_history_ui import EnrollmentHistoryUI  # Asegúrate de tener este archivo

class EnrollmentManagementUI(tk.Toplevel):
    def __init__(self, root, student_controller, course_controller):
        super().__init__(root)
        self.root = root
        self.student_controller = student_controller
        self.course_controller = course_controller
        self.db = self.student_controller.db  # Asignar la instancia de base de datos
        # Crear la instancia del EnrollmentController utilizando la conexión de student_controller
        self.enrollment_controller = EnrollmentController(self.db, self.student_controller, self.course_controller)
        self.title("Gestión de Inscripciones")
        self.geometry("700x500")
        self.create_widgets()
        self.load_enrollments()

    def create_widgets(self):
        # Treeview para mostrar las inscripciones del año académico actual
        self.tree = ttk.Treeview(
            self, 
            columns=("id", "student_id", "course", "academic_year", "status"), 
            show="headings"
        )
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
        
        # Vincular doble clic para abrir la ventana de historial de inscripciones
        self.tree.bind("<Double-1>", self.on_row_double_click)
        
        # Frame para actualizar el estado de la inscripción seleccionada
        btn_frame = ttk.Frame(self)
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
        Al hacer doble clic en una inscripción, se abre una ventana que muestra el historial
        completo de inscripciones del estudiante correspondiente.
        """
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        student_id = item["values"][1]  # Suponemos que la segunda columna es el ID del estudiante
        # Pasa además student_controller y course_controller a EnrollmentHistoryUI
        EnrollmentHistoryUI(self.root, self.db, self.student_controller, self.course_controller, student_id)

    def process_enrollment(self):
        """
        Permite al administrador actualizar el estado de la inscripción seleccionada.
        Si se marca como "promovido", se:
         - Actualiza el estado de la inscripción actual.
         - Determina el siguiente curso utilizando get_next_course.
         - Actualiza el curso actual del estudiante en la tabla 'estudiantes'.
         - Crea una nueva inscripción para el siguiente año académico.
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección requerida", "Por favor, seleccione una inscripción para procesar.")
            return
        
        enrollment_item = self.tree.item(selected[0])
        enrollment_id = enrollment_item["values"][0]
        current_student_id = enrollment_item["values"][1]
        new_status = self.status_var.get()
        
        # Actualizar el estado de la inscripción actual
        success, msg = self.enrollment_controller.update_enrollment_status(enrollment_id, new_status)
        if not success:
            messagebox.showerror("Error", msg)
            return

        if new_status.lower() == "promovido":
            # Buscar la inscripción actual en el historial
            all_enrollments = self.enrollment_controller.get_all_enrollments()
            current_enrollment = None
            for enr in all_enrollments:
                if enr.get("id") == enrollment_id:
                    current_enrollment = enr
                    break
            if current_enrollment:
                current_course_id = current_enrollment.get("course_id")
                course_data = self.course_controller.get_course_by_id(current_course_id)
                if course_data:
                    current_course_name = course_data.get("name", "")
                    # Obtener el siguiente curso usando la función auxiliar
                    next_course_name = get_next_course(current_course_name)
                    # Buscar entre los cursos activos el curso cuyo nombre coincida (sin considerar sección)
                    active_courses = self.course_controller.get_active_courses()
                    next_course_id = None
                    for course in active_courses:
                        if course.get("name", "").lower() == next_course_name.lower():
                            next_course_id = course.get("id")
                            break
                    if next_course_id:
                        # Actualizar el curso actual del estudiante en la tabla 'estudiantes'
                        update_success, update_msg = self.student_controller.update_student_course(current_student_id, next_course_id)
                        if update_success:
                            # Crear nueva inscripción para el siguiente año académico
                            next_year = current_enrollment.get("academic_year", datetime.datetime.now().year) + 1
                            enroll_success, enroll_msg, new_enrollment_id = self.enrollment_controller.create_enrollment(
                                current_student_id, next_course_id, next_year, status="inscrito"
                            )
                            if enroll_success:
                                messagebox.showinfo("Éxito", "Estudiante promovido y nueva inscripción creada para el siguiente año académico.")
                            else:
                                messagebox.showerror("Error", f"No se pudo crear la nueva inscripción: {enroll_msg}")
                        else:
                            messagebox.showerror("Error", f"No se pudo actualizar el curso del estudiante: {update_msg}")
                    else:
                        messagebox.showwarning("Información", "No se encontró el curso siguiente en la lista de cursos activos.")
                else:
                    messagebox.showwarning("Información", "No se pudieron obtener los datos del curso actual.")
            else:
                messagebox.showwarning("Información", "No se pudo obtener la inscripción actual.")
        else:
            messagebox.showinfo("Éxito", "Inscripción actualizada.")
        
        self.load_enrollments()

if __name__ == "__main__":
    import sqlite3
    db = sqlite3.connect("colegio.db")
    db.row_factory = sqlite3.Row
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    ui = EnrollmentManagementUI(db)
    root.mainloop()

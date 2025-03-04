# src/views/update_student_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from src.controllers.student_controller import StudentController
from src.controllers.course_controller import CourseController
from src.controllers.user_controller import UserController

class UpdateStudentWindow(tk.Toplevel):
    def __init__(self, master, student, student_controller, course_controller, user_controller):
        """
        Ventana para actualizar el curso, representante y teléfono del representante de un estudiante.
        Se requiere la contraseña del administrador para efectuar la actualización.
        
        :param master: Ventana padre.
        :param student: Diccionario con los datos del estudiante.
        :param student_controller: Instancia de StudentController.
        :param course_controller: Instancia de CourseController.
        :param user_controller: Instancia de UserController para validar la contraseña de admin.
        """
        super().__init__(master)
        self.student = student
        self.student_controller = student_controller
        self.course_controller = course_controller
        self.user_controller = user_controller
        self.title("Actualizar Datos del Estudiante")
        self.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="20")
        frame.pack(expand=True, fill="both")
        
        # Campo para seleccionar Curso
        ttk.Label(frame, text="Curso:").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_course = ttk.Combobox(frame, state="readonly", width=30)
        self.combo_course.grid(row=0, column=1, pady=5)
        
        # Obtener cursos y configurar combobox
        courses = self.course_controller.get_all_courses()
        self.course_map = {}
        course_names = []
        for course in courses:
            if course.get("seccion") and course["seccion"].strip():
                display_name = f"{course['name']} - {course['seccion']}"
            else:
                display_name = course["name"]
            course_names.append(display_name)
            self.course_map[display_name] = course["id"]
        self.combo_course["values"] = course_names
        # Seleccionar el curso actual del estudiante
        current_course = self.student.get("course_name", "")
        if current_course in self.course_map:
            self.combo_course.set(current_course)
        else:
            self.combo_course.set(course_names[0] if course_names else "")
        
        # Campo para actualizar Representante
        ttk.Label(frame, text="Representante:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_representative = ttk.Entry(frame, width=30)
        self.entry_representative.grid(row=1, column=1, pady=5)
        self.entry_representative.insert(0, self.student.get("representante", ""))
        
        # Campo para actualizar Teléfono
        ttk.Label(frame, text="Teléfono:").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_phone = ttk.Entry(frame, width=30)
        self.entry_phone.grid(row=2, column=1, pady=5)
        self.entry_phone.insert(0, self.student.get("telefono", ""))
        
        # Campo para la contraseña de administrador
        ttk.Label(frame, text="Contraseña Admin:").grid(row=3, column=0, sticky="w", pady=5)
        self.entry_admin_pass = ttk.Entry(frame, show="*", width=30)
        self.entry_admin_pass.grid(row=3, column=1, pady=5)
        
        # Botón Guardar
        btn_save = ttk.Button(frame, text="Guardar", command=self.save_updates)
        btn_save.grid(row=4, column=0, columnspan=2, pady=15)

    def save_updates(self):
        selected_course = self.combo_course.get()
        new_course_id = self.course_map.get(selected_course)
        new_representative = self.entry_representative.get().strip()
        new_phone = self.entry_phone.get().strip()
        admin_pass = self.entry_admin_pass.get().strip()
        
        if not admin_pass:
            messagebox.showwarning("Campos incompletos", "Debe ingresar la contraseña de administrador.")
            return
        
        # Validar credenciales de administrador (se asume que el usuario admin es "admin")
        admin_user = self.user_controller.login("admin", admin_pass)
        if not admin_user or admin_user.role.lower() != "admin":
            messagebox.showerror("Error", "Contraseña de administrador incorrecta.")
            return
        
        # Actualizar la información del estudiante
        success, msg = self.student_controller.update_student_info(self.student["id"], new_course_id, new_representative, new_phone)
        if success:
            messagebox.showinfo("Éxito", msg)
            self.destroy()
        else:
            messagebox.showerror("Error", msg)

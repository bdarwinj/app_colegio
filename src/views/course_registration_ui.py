import tkinter as tk
from tkinter import ttk, messagebox

class CourseRegistrationUI(tk.Toplevel):
    """
    Interfaz para registrar un nuevo curso.
    """
    def __init__(self, master, course_controller):
        """
        Inicializa la ventana de registro de curso.
        
        :param master: Ventana padre.
        :param course_controller: Controlador de cursos para registrar el nuevo curso.
        """
        super().__init__(master)
        self.course_controller = course_controller
        self.title("Registrar Nuevo Curso")
        self.geometry("400x250")
        self.create_widgets()

    def create_widgets(self):
        """
        Crea y organiza los widgets de la interfaz.
        """
        frame = ttk.Frame(self, padding=20)
        frame.pack(expand=True, fill="both")
        
        # Campo para el nombre del curso
        ttk.Label(frame, text="Nombre del Curso:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_name = ttk.Entry(frame, width=40)
        self.entry_name.grid(row=0, column=1, pady=5)
        
        # Campo para la descripción del curso
        ttk.Label(frame, text="Descripción:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_description = ttk.Entry(frame, width=40)
        self.entry_description.grid(row=1, column=1, pady=5)
        
        # Botón para registrar el curso
        self.btn_register = ttk.Button(frame, text="Registrar Curso", command=self.register_course)
        self.btn_register.grid(row=2, column=0, columnspan=2, pady=15)
        
        frame.columnconfigure(1, weight=1)

    def register_course(self):
        """
        Registra un nuevo curso utilizando el course_controller.
        Valida que el nombre del curso no esté vacío y muestra mensajes informativos.
        """
        course_name = self.entry_name.get().strip()
        description = self.entry_description.get().strip()
        
        if not course_name:
            messagebox.showwarning("Campos incompletos", "El nombre del curso es obligatorio.")
            return
        
        success, msg = self.course_controller.register_course(course_name, description)
        if success:
            messagebox.showinfo("Éxito", msg)
            self.destroy()
        else:
            messagebox.showerror("Error", msg)
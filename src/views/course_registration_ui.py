import tkinter as tk
from tkinter import ttk, messagebox

class CourseRegistrationUI(tk.Toplevel):
    def __init__(self, master, course_controller):
        super().__init__(master)
        self.course_controller = course_controller
        self.title("Registrar Nuevo Curso")
        self.geometry("400x250")
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(expand=True, fill="both")
        
        ttk.Label(frame, text="Nombre del Curso:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_name = ttk.Entry(frame, width=40)
        self.entry_name.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Descripción:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_description = ttk.Entry(frame, width=40)
        self.entry_description.grid(row=1, column=1, pady=5)
        
        # Puedes agregar más campos según la lógica del sistema
        
        self.btn_register = ttk.Button(frame, text="Registrar Curso", command=self.register_course)
        self.btn_register.grid(row=2, column=0, columnspan=2, pady=15)
        
        frame.columnconfigure(1, weight=1)

    def register_course(self):
        course_name = self.entry_name.get().strip()
        description = self.entry_description.get().strip()
        
        if not course_name:
            messagebox.showwarning("Campos incompletos", "El nombre del curso es obligatorio.")
            return
        
        # Llamada al método del course_controller (ajusta parámetros según tu implementación)
        success, msg = self.course_controller.register_course(course_name, description)
        if success:
            messagebox.showinfo("Éxito", msg)
            self.destroy()
        else:
            messagebox.showerror("Error", msg)
# src/views/course_fee_config_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from src.controllers.course_fee_controller import CourseFeeController

class CourseFeeConfigWindow(tk.Toplevel):
    def __init__(self, master, db, course_controller):
        """
        Ventana para configurar la tarifa (mensualidad) para cada curso en un año académico.
        :param master: Ventana padre.
        :param db: Conexión a la base de datos.
        :param course_controller: Instancia de CourseController para obtener la lista de cursos.
        """
        super().__init__(master)
        self.db = db
        self.course_controller = course_controller
        self.course_fee_controller = CourseFeeController(db)
        self.title("Configurar Tarifas de Cursos")
        self.geometry("500x400")
        self.create_widgets()
        self.load_courses()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="20")
        frame.pack(expand=True, fill="both")
        
        ttk.Label(frame, text="Curso:").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_course = ttk.Combobox(frame, state="readonly", width=30)
        self.combo_course.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Año Académico:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_year = ttk.Entry(frame, width=30)
        self.entry_year.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Tarifa (Mensualidad):").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_fee = ttk.Entry(frame, width=30)
        self.entry_fee.grid(row=2, column=1, pady=5)
        
        btn_save = ttk.Button(frame, text="Guardar", command=self.save_fee)
        btn_save.grid(row=3, column=0, columnspan=2, pady=15)
        
        # Opcional: Listado de tarifas para el año ingresado
        self.tree = ttk.Treeview(frame, columns=("course", "year", "fee"), show="headings", height=5)
        self.tree.heading("course", text="Curso")
        self.tree.heading("year", text="Año")
        self.tree.heading("fee", text="Tarifa")
        self.tree.grid(row=4, column=0, columnspan=2, pady=10, sticky="nsew")
        frame.rowconfigure(4, weight=1)

    def load_courses(self):
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
        if course_names:
            self.combo_course.set(course_names[0])

    def save_fee(self):
        course_name = self.combo_course.get()
        try:
            academic_year = int(self.entry_year.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Ingrese un año académico válido.")
            return
        try:
            fee = float(self.entry_fee.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Ingrese una tarifa válida.")
            return
        course_id = self.course_map.get(course_name)
        success, msg = self.course_fee_controller.set_fee(course_id, academic_year, fee)
        if success:
            messagebox.showinfo("Éxito", msg)
            self.load_fee_list(academic_year)
        else:
            messagebox.showerror("Error", msg)

    def load_fee_list(self, academic_year):
        fees = self.course_fee_controller.get_all_fees(academic_year)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for fee_item in fees:
            # Se muestra el curso (aquí se puede mejorar para mostrar el nombre completo usando course_controller)
            self.tree.insert("", "end", values=(fee_item.get("course_id"), fee_item.get("academic_year"), fee_item.get("fee")))

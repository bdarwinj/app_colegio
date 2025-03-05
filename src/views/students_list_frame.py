# src/views/students_list_frame.py
import tkinter as tk
from tkinter import ttk

class StudentsListFrame(ttk.LabelFrame):
    def __init__(self, parent, student_controller, double_click_command):
        super().__init__(parent, text="Lista de Estudiantes")
        self.student_controller = student_controller
        self.double_click_command = double_click_command
        self.all_students = self.student_controller.get_all_students()
        self.filtered_students = self.all_students.copy()  # Lista para la búsqueda
        self.page_size = 10  # Número de estudiantes por página (ajustable)
        self.current_page = 1
        self.create_widgets()

    def create_widgets(self):
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(search_frame, text="Buscar:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.on_search_students)
        
        self.columns = ("id", "identificacion", "nombre", "apellido", "curso")
        self.tree = ttk.Treeview(self, columns=self.columns, show="headings")
        for col in self.columns:
            self.tree.heading(col, text=col.capitalize(), command=lambda _col=col: self.sort_by(_col))
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.double_click_command)
        
        # Frame de paginación
        pagination_frame = ttk.Frame(self)
        pagination_frame.pack(fill="x", pady=5)
        self.btn_prev = ttk.Button(pagination_frame, text="Anterior", command=self.prev_page)
        self.btn_prev.pack(side="left", padx=5)
        self.page_label = ttk.Label(pagination_frame, text="Página 1 de 1")
        self.page_label.pack(side="left", padx=5)
        self.btn_next = ttk.Button(pagination_frame, text="Siguiente", command=self.next_page)
        self.btn_next.pack(side="left", padx=5)
        
        self.populate_student_list(self.filtered_students)

    def on_search_students(self, event):
        query = self.search_var.get().lower().strip()
        if query:
            self.filtered_students = [stu for stu in self.all_students if query in str(stu["identificacion"]).lower() 
                        or query in stu["nombre"].lower() 
                        or query in stu["apellido"].lower()]
        else:
            self.filtered_students = self.all_students.copy()
        self.current_page = 1
        self.populate_student_list(self.filtered_students)

    def populate_student_list(self, students):
        # Limpiar el Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        total_students = len(students)
        total_pages = (total_students + self.page_size - 1) // self.page_size
        if total_pages == 0:
            total_pages = 1
        
        # Obtener la porción de estudiantes para la página actual
        start_index = (self.current_page - 1) * self.page_size
        end_index = start_index + self.page_size
        page_students = students[start_index:end_index]
        
        for est in page_students:
            course_name = est.get("course_name", "N/A")
            self.tree.insert("", "end", values=(est["id"], est["identificacion"], est["nombre"], est["apellido"], course_name))
        
        self.update_pagination_controls(total_pages)

    def update_pagination_controls(self, total_pages):
        self.page_label.config(text=f"Página {self.current_page} de {total_pages}")
        self.btn_prev.config(state="normal" if self.current_page > 1 else "disabled")
        self.btn_next.config(state="normal" if self.current_page < total_pages else "disabled")

    def next_page(self):
        total_students = len(self.filtered_students)
        total_pages = (total_students + self.page_size - 1) // self.page_size
        if self.current_page < total_pages:
            self.current_page += 1
            self.populate_student_list(self.filtered_students)

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.populate_student_list(self.filtered_students)

    def sort_by(self, col):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        try:
            data.sort(key=lambda t: float(t[0]))
        except ValueError:
            data.sort(key=lambda t: t[0])
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)
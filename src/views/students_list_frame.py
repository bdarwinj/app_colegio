import tkinter as tk
from tkinter import ttk

class StudentsListFrame(ttk.LabelFrame):
    def __init__(self, parent, student_controller, double_click_command):
        super().__init__(parent, text="Lista de Estudiantes")
        self.student_controller = student_controller
        self.double_click_command = double_click_command
        self.all_students = self.student_controller.get_all_students()
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
        self.populate_student_list(self.all_students)

    def on_search_students(self, event):
        query = self.search_var.get().lower().strip()
        if query:
            filtered = [stu for stu in self.all_students if query in str(stu["identificacion"]).lower() 
                        or query in stu["nombre"].lower() 
                        or query in stu["apellido"].lower()]
        else:
            filtered = self.all_students
        self.populate_student_list(filtered)

    def populate_student_list(self, students):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for est in students:
            course_name = est.get("course_name", "N/A")
            self.tree.insert("", "end", values=(est["id"], est["identificacion"], est["nombre"], est["apellido"], course_name))

    def sort_by(self, col):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        try:
            data.sort(key=lambda t: float(t[0]))
        except ValueError:
            data.sort(key=lambda t: t[0])
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)
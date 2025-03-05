import tkinter as tk
from tkinter import ttk, messagebox

class CourseManagementWindow(tk.Toplevel):
    def __init__(self, parent, course_controller):
        super().__init__(parent)
        self.course_controller = course_controller
        self.title("Administración de Cursos")
        self.geometry("400x400")
        self.create_widgets()

    def create_widgets(self):
        # Sección de lista de cursos
        frame_list = ttk.LabelFrame(self, text="Cursos Existentes")
        frame_list.pack(padx=10, pady=10, fill="both", expand=True)
        self.courses_tree = ttk.Treeview(frame_list, columns=("id", "name", "active"), show="headings")
        self.courses_tree.heading("id", text="ID")
        self.courses_tree.heading("name", text="Nombre")
        self.courses_tree.heading("active", text="Activo")
        self.courses_tree.pack(fill="both", expand=True)
        self.load_courses_into_tree()

        # Sección para agregar/editar curso
        frame_form = ttk.LabelFrame(self, text="Agregar / Editar Curso")
        frame_form.pack(padx=10, pady=10, fill="x")
        ttk.Label(frame_form, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_course_name = ttk.Entry(frame_form)
        self.entry_course_name.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(frame_form, text="Sección (opcional):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_course_section = ttk.Entry(frame_form)
        self.entry_course_section.grid(row=1, column=1, padx=5, pady=5)

        btn_add = ttk.Button(frame_form, text="Agregar", command=self.add_course)
        btn_add.grid(row=2, column=0, padx=5, pady=5)
        btn_edit = ttk.Button(frame_form, text="Editar", command=self.edit_course)
        btn_edit.grid(row=2, column=1, padx=5, pady=5)
        btn_deactivate = ttk.Button(frame_form, text="Desactivar", command=self.deactivate_course)
        btn_deactivate.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def load_courses_into_tree(self):
        # Eliminar ítems existentes y recargar la lista
        for item in self.courses_tree.get_children():
            self.courses_tree.delete(item)
        courses = self.course_controller.get_all_courses()
        for course in courses:
            full_name = (f"{course['name']} - {course['seccion']}"
                         if course.get("seccion") and course["seccion"].strip() 
                         else course["name"])
            active_text = "Sí" if course["active"] == 1 else "No"
            self.courses_tree.insert("", "end", values=(course["id"], full_name, active_text))

    def add_course(self):
        name = self.entry_course_name.get().strip()
        section = self.entry_course_section.get().strip()
        if not name:
            messagebox.showwarning("Campos incompletos", "Ingrese el nombre del curso.")
            return
        success, msg = self.course_controller.add_course(name, section)
        if success:
            messagebox.showinfo("Éxito", msg)
            self.load_courses_into_tree()
            self.entry_course_name.delete(0, tk.END)
            self.entry_course_section.delete(0, tk.END)
        else:
            messagebox.showerror("Error", msg)

    def edit_course(self):
        selected = self.courses_tree.selection()
        if not selected:
            messagebox.showwarning("Selección requerida", "Seleccione un curso para editar.")
            return
        course_item = self.courses_tree.item(selected[0])
        course_id = course_item["values"][0]
        new_name = self.entry_course_name.get().strip()
        new_section = self.entry_course_section.get().strip()
        if not new_name:
            messagebox.showwarning("Campos incompletos", "Ingrese el nuevo nombre del curso.")
            return
        success, msg = self.course_controller.edit_course(course_id, new_name, new_section)
        if success:
            messagebox.showinfo("Éxito", msg)
            self.load_courses_into_tree()
            self.entry_course_name.delete(0, tk.END)
            self.entry_course_section.delete(0, tk.END)
        else:
            messagebox.showerror("Error", msg)

    def deactivate_course(self):
        selected = self.courses_tree.selection()
        if not selected:
            messagebox.showwarning("Selección requerida", "Seleccione un curso para desactivar.")
            return
        course_item = self.courses_tree.item(selected[0])
        course_id = course_item["values"][0]
        confirm = messagebox.askyesno("Confirmar", "¿Está seguro de desactivar el curso?")
        if confirm:
            success, msg = self.course_controller.deactivate_course(course_id)
            if success:
                messagebox.showinfo("Éxito", msg)
                self.load_courses_into_tree()
            else:
                messagebox.showerror("Error", msg)
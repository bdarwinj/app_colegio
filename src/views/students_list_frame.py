import tkinter as tk
from tkinter import ttk

class StudentsListFrame(ttk.LabelFrame):
    def __init__(self, parent, student_controller, double_click_command):
        """
        Inicializa el frame de la lista de estudiantes.

        :param parent: Widget padre.
        :param student_controller: Controlador para obtener estudiantes.
        :param double_click_command: Comando a ejecutar al hacer doble clic en un estudiante.
        """
        super().__init__(parent, text="Lista de Estudiantes")
        self.student_controller = student_controller
        self.double_click_command = double_click_command
        self.all_students = self.student_controller.get_all_students()
        self.create_widgets()

    def create_widgets(self):
        """Crea y organiza los widgets del frame."""
        # Frame para la búsqueda de estudiantes
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(search_frame, text="Buscar:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.on_search_students)
        
        # Configuración del Treeview
        self.columns = ("id", "identificacion", "nombre", "apellido", "curso")
        self.tree = ttk.Treeview(self, columns=self.columns, show="headings")
        for col in self.columns:
            # Utiliza un lambda con argumento por defecto para mantener el valor de _col
            self.tree.heading(col, text=col.capitalize(), command=lambda _col=col: self.sort_by(_col))
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.double_click_command)
        
        # Poblar la lista de estudiantes
        self.populate_student_list(self.all_students)

    def on_search_students(self, event):
        """Filtra la lista de estudiantes según la consulta ingresada."""
        query = self.search_var.get().lower().strip()
        if query:
            filtered = [
                stu for stu in self.all_students
                if query in str(stu.get("identificacion", "")).lower() or
                   query in stu.get("nombre", "").lower() or
                   query in stu.get("apellido", "").lower()
            ]
        else:
            filtered = self.all_students
        self.populate_student_list(filtered)

    def populate_student_list(self, students):
        """Limpia el Treeview y lo repuebla con la lista de estudiantes proporcionada."""
        # Limpiar el Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Insertar cada estudiante en el Treeview
        for est in students:
            course_name = est.get("course_name", "N/A")
            self.tree.insert("", "end", values=(
                est.get("id", ""),
                est.get("identificacion", ""),
                est.get("nombre", ""),
                est.get("apellido", ""),
                course_name
            ))

    def sort_by(self, col):
        """
        Ordena las filas del Treeview basándose en la columna indicada.

        Intenta convertir los valores a float para ordenar numéricamente, 
        si falla ordena como texto.
        """
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children()]
        try:
            data.sort(key=lambda t: float(t[0]) if t[0] else 0)
        except ValueError:
            data.sort(key=lambda t: t[0])
        # Reubicar los elementos en el Treeview en el orden correcto
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)
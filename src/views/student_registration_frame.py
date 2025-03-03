import tkinter as tk
from tkinter import ttk, messagebox

class StudentRegistrationFrame(ttk.LabelFrame):
    def __init__(self, parent, course_controller, register_command):
        """
        Inicializa el frame para registrar estudiantes.
        
        :param parent: Widget padre.
        :param course_controller: Controlador para manejar cursos.
        :param register_command: Comando para registrar el estudiante.
        """
        super().__init__(parent, text="Registrar Estudiante")
        self.course_controller = course_controller
        self.register_command = register_command
        self.entries = {}
        self.combo_course = None
        self.course_map = {}
        self.create_widgets()

    def create_widgets(self):
        """Crea y organiza los widgets del formulario de registro."""
        self._create_text_entries()
        self._create_course_combobox()
        self._create_register_button()

    def _create_text_entries(self):
        """Crea las entradas de texto para los datos del estudiante."""
        labels = ["Número de Identificación", "Nombre", "Apellido", "Representante", "Teléfono"]
        
        def validate_numeric(P):
            return P.isdigit() or P == ""
        
        vcmd = (self.register(validate_numeric), '%P')
        
        # Función para convertir el texto a mayúsculas al perder el foco
        def on_focusout_upper(event):
            content = event.widget.get()
            event.widget.delete(0, tk.END)
            event.widget.insert(0, content.upper())
        
        def on_focusout_numeric(event):
            if event.widget.get().strip() == "":
                messagebox.showwarning("Campos incompletos", "Este campo es obligatorio y debe ser numérico.")
                event.widget.focus_set()

        for idx, text in enumerate(labels):
            ttk.Label(self, text=f"{text}:").grid(row=idx, column=0, sticky="w", padx=5, pady=5)
            if text in ["Número de Identificación", "Teléfono"]:
                entry = ttk.Entry(self, validate="key", validatecommand=vcmd)
                entry.bind("<FocusOut>", on_focusout_numeric)
            else:
                entry = ttk.Entry(self)
                # Para los campos Nombre, Apellido y Representante se añade la conversión a mayúsculas
                if text in ["Nombre", "Apellido", "Representante"]:
                    entry.bind("<FocusOut>", on_focusout_upper)
            entry.grid(row=idx, column=1, padx=5, pady=5)
            self.entries[text] = entry

    def _create_course_combobox(self):
        """Crea el combobox para seleccionar el curso."""
        labels = ["Número de Identificación", "Nombre", "Apellido", "Representante", "Teléfono"]
        ttk.Label(self, text="Curso:").grid(row=len(labels), column=0, sticky="w", padx=5, pady=5)
        self.combo_course = ttk.Combobox(self, state="readonly")
        self.combo_course.grid(row=len(labels), column=1, padx=5, pady=5)
        # No cargamos los cursos aquí porque se hace desde AppUI

    def _create_register_button(self):
        """Crea el botón para registrar el estudiante."""
        labels = ["Número de Identificación", "Nombre", "Apellido", "Representante", "Teléfono"]
        self.btn_registrar = ttk.Button(self, text="Registrar Estudiante", command=self.register_command)
        self.btn_registrar.grid(row=len(labels) + 1, column=0, columnspan=2, pady=10)

    def populate_courses(self):
        """
        Obtiene la lista de cursos usando el course_controller y configura
        el combobox y el course_map para mapear el nombre del curso (con sección, si existe) a su ID.
        """
        courses = self.course_controller.get_all_courses()  # Asegúrate de que este método exista y retorne la info necesaria
        course_names = []
        self.course_map = {}
        for course in courses:
            # Se asume que cada curso es un diccionario con las claves "id", "name" y opcionalmente "seccion"
            if course.get("seccion") and course["seccion"].strip():
                display_name = f"{course['name']} - {course['seccion']}"
            else:
                display_name = course["name"]
            course_names.append(display_name)
            self.course_map[display_name] = course["id"]
        self.combo_course["values"] = course_names
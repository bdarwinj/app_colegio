import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from fpdf import FPDF
import datetime
import traceback
from src.controllers.student_controller import StudentController
from src.controllers.course_controller import CourseController
from src.controllers.config_controller import ConfigController
from src.controllers.user_controller import UserController
from src.views.config_ui import ConfigUI
from src.views.user_management_ui import UserManagementUI
from src.views.payment_ui import PaymentUI
from src.views.login_ui import LoginUI
from config import SCHOOL_NAME, LOGO_PATH
from src.views.student_details_window import StudentDetailsWindow  # Import for student details

class AppUI:
    def __init__(self, db, user):
        self.db = db
        self.user = user
        self.student_controller = StudentController(self.db)
        self.course_controller = CourseController(self.db)
        self.config_controller = ConfigController(db)
        self.user_controller = UserController(self.db)
        self.root = tk.Tk()
        # Load configuration for school name and logo
        configs = self.config_controller.get_all_configs()
        school_name = configs.get("SCHOOL_NAME", SCHOOL_NAME)
        logo_path = configs.get("LOGO_PATH", LOGO_PATH)
        self.abs_logo_path = os.path.abspath(logo_path)
        self.root.title(f"{school_name} - Sistema de Pagos (Usuario: {self.user.username})")
        self.root.geometry("900x650")
        self.create_widgets()

    def create_widgets(self):
        # Header with logo, name, and logout button
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=10, pady=10)
        # Logo
        if os.path.exists(self.abs_logo_path):
            try:
                image = Image.open(self.abs_logo_path)
                image = image.resize((80, 80), Image.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(image)
                logo_label = ttk.Label(header_frame, image=self.logo_image)
                logo_label.pack(side="left", padx=5)
            except Exception as e:
                print(f"Error al cargar el logo: {e}")
        else:
            print(f"No se encontró la imagen en: {self.abs_logo_path}")
        # School Name
        name_label = ttk.Label(header_frame, text=self.root.title(), font=("Arial", 18, "bold"))
        name_label.pack(side="left", padx=10)
        # Logout Button
        btn_logout = ttk.Button(header_frame, text="Cerrar Sesión", command=self.logout)
        btn_logout.pack(side="right", padx=10)

        # Admin Panel
        if self.user.role == "admin":
            self.create_admin_panel()
        
        # Student Registration Frame
        self.frame_form = ttk.LabelFrame(self.root, text="Registrar Estudiante")
        self.frame_form.pack(padx=10, pady=10, fill="x")
        if self.user.role != "admin":
            self.frame_form.configure(text="Registrar Estudiante (Solo Admin)")
        
        labels = ["Número de Identificación", "Nombre", "Apellido", "Representante", "Teléfono"]
        self.entries = {}
        for idx, text in enumerate(labels):
            ttk.Label(self.frame_form, text=f"{text}:").grid(row=idx, column=0, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(self.frame_form)
            entry.grid(row=idx, column=1, padx=5, pady=5)
            self.entries[text] = entry

        # Course Combobox
        ttk.Label(self.frame_form, text="Curso:").grid(row=len(labels), column=0, sticky="w", padx=5, pady=5)
        self.combo_course = ttk.Combobox(self.frame_form, state="readonly")
        self.combo_course.grid(row=len(labels), column=1, padx=5, pady=5)
        self.load_courses_into_combobox()

        self.btn_registrar = ttk.Button(self.frame_form, text="Registrar Estudiante", command=self.registrar_estudiante)
        self.btn_registrar.grid(row=len(labels)+1, column=0, columnspan=2, pady=10)
        if self.user.role != "admin":
            self.btn_registrar.configure(state="disabled")

        # Students List Frame
        self.frame_lista = ttk.LabelFrame(self.root, text="Lista de Estudiantes")
        self.frame_lista.pack(padx=10, pady=10, fill="both", expand=True)
        columnas = ("id", "identificacion", "nombre", "apellido", "curso")
        self.tree = ttk.Treeview(self.frame_lista, columns=columnas, show="headings")
        for col in columnas:
            self.tree.heading(col, text=col.capitalize())
        self.tree.pack(fill="both", expand=True)
        # Bind double-click event on the treeview to open student details using identification number.
        self.tree.bind("<Double-1>", self.on_student_double_click)

        # Action Buttons
        self.btn_refrescar = ttk.Button(self.root, text="Refrescar Lista", command=self.refrescar_lista)
        self.btn_refrescar.pack(pady=5)
        self.btn_pdf = ttk.Button(self.root, text="Generar Paz y Salvo", command=self.generar_pdf)
        self.btn_pdf.pack(pady=5)

    def create_admin_panel(self):
        self.frame_admin = ttk.LabelFrame(self.root, text="Panel de Administración")
        self.frame_admin.pack(padx=10, pady=10, fill="x")
        self.btn_config = ttk.Button(self.frame_admin, text="Editar Configuración", command=self.editar_configuracion)
        self.btn_config.pack(side="left", padx=5, pady=5)
        self.btn_registrar_pago = ttk.Button(self.frame_admin, text="Registrar Pago", command=self.registrar_pago)
        self.btn_registrar_pago.pack(side="left", padx=5, pady=5)
        self.btn_cursos = ttk.Button(self.frame_admin, text="Administrar Cursos", command=self.manage_courses)
        self.btn_cursos.pack(side="left", padx=5, pady=5)
        self.btn_usuarios = ttk.Button(self.frame_admin, text="Administrar Usuarios", command=self.manage_users)
        self.btn_usuarios.pack(side="left", padx=5, pady=5)

    def editar_configuracion(self):
        ConfigUI(self.db)

    def registrar_pago(self):
        from src.views.payment_ui import PaymentUI
        PaymentUI(self.db)

    def manage_courses(self):
        win = tk.Toplevel(self.root)
        win.title("Administración de Cursos")
        win.geometry("400x400")
        frame_list = ttk.LabelFrame(win, text="Cursos Existentes")
        frame_list.pack(padx=10, pady=10, fill="both", expand=True)
        self.courses_tree = ttk.Treeview(frame_list, columns=("id", "name", "active"), show="headings")
        self.courses_tree.heading("id", text="ID")
        self.courses_tree.heading("name", text="Nombre")
        self.courses_tree.heading("active", text="Activo")
        self.courses_tree.pack(fill="both", expand=True)
        self.load_courses_into_tree()
        frame_form = ttk.LabelFrame(win, text="Agregar / Editar Curso")
        frame_form.pack(padx=10, pady=10, fill="x")
        ttk.Label(frame_form, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_course_name = ttk.Entry(frame_form)
        self.entry_course_name.grid(row=0, column=1, padx=5, pady=5)
        btn_add = ttk.Button(frame_form, text="Agregar", command=self.add_course)
        btn_add.grid(row=1, column=0, padx=5, pady=5)
        btn_edit = ttk.Button(frame_form, text="Editar", command=self.edit_course)
        btn_edit.grid(row=1, column=1, padx=5, pady=5)
        btn_deactivate = ttk.Button(frame_form, text="Desactivar", command=self.deactivate_course)
        btn_deactivate.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    def manage_users(self):
        from src.views.user_management_ui import UserManagementUI
        UserManagementUI(self.db)

    def load_courses_into_tree(self):
        for item in self.courses_tree.get_children():
            self.courses_tree.delete(item)
        courses = self.course_controller.get_all_courses()
        for course in courses:
            self.courses_tree.insert("", "end", values=(course["id"], course["name"], "Sí" if course["active"] == 1 else "No"))
        self.load_courses_into_combobox()

    def add_course(self):
        name = self.entry_course_name.get().strip()
        if not name:
            messagebox.showwarning("Campos incompletos", "Ingrese el nombre del curso.")
            return
        success, msg = self.course_controller.add_course(name)
        if success:
            messagebox.showinfo("Éxito", msg)
            self.load_courses_into_tree()
            self.entry_course_name.delete(0, tk.END)
        else:
            messagebox.showerror("Error", msg)

    def edit_course(self):
        selected = self.courses_tree.selection()
        if not selected:
            messagebox.showwarning("Sin selección", "Seleccione un curso para editar.")
            return
        course_item = self.courses_tree.item(selected[0])
        course_id = course_item["values"][0]
        new_name = self.entry_course_name.get().strip()
        if not new_name:
            messagebox.showwarning("Campos incompletos", "Ingrese el nuevo nombre del curso.")
            return
        success, msg = self.course_controller.edit_course(course_id, new_name)
        if success:
            messagebox.showinfo("Éxito", msg)
            self.load_courses_into_tree()
            self.entry_course_name.delete(0, tk.END)
        else:
            messagebox.showerror("Error", msg)

    def deactivate_course(self):
        selected = self.courses_tree.selection()
        if not selected:
            messagebox.showwarning("Sin selección", "Seleccione un curso para desactivar.")
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

    def load_courses_into_combobox(self):
        courses = self.course_controller.get_active_courses()
        course_names = []
        course_ids = []
        for course in courses:
            course_names.append(course["name"])
            course_ids.append(course["id"])
        self.combo_course["values"] = course_names
        self.course_map = dict(zip(course_names, course_ids))

    def registrar_estudiante(self):
        identificacion = self.entries["Número de Identificación"].get()
        nombre = self.entries["Nombre"].get()
        apellido = self.entries["Apellido"].get()
        representante = self.entries["Representante"].get()
        telefono = self.entries["Teléfono"].get()
        course_name = self.combo_course.get()
        if not (identificacion and nombre and apellido and representante and telefono and course_name):
            messagebox.showwarning("Campos incompletos", "Por favor, llene todos los campos.")
            return
        course_id = self.course_map.get(course_name)
        success, msg = self.student_controller.register_student(
            identificacion, nombre, apellido, course_id, representante, telefono)
        if success:
            messagebox.showinfo("Éxito", msg)
            self.limpiar_formulario()
            self.refrescar_lista()
        else:
            messagebox.showerror("Error", msg)

    def limpiar_formulario(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.combo_course.set("")

    def refrescar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        estudiantes = self.student_controller.get_all_students()
        for est in estudiantes:
            course_name = est["course_name"] if est["course_name"] else "N/A"
            self.tree.insert("", "end", values=(est["id"], est["identificacion"], est["nombre"], est["apellido"], course_name))

    def on_student_double_click(self, event):
        try:
            selected = self.tree.selection()
            if selected:
                item = self.tree.item(selected[0])
                # Retrieve the student's identification number (column index 1)
                student_identificacion = item["values"][1]
                StudentDetailsWindow(self.db, student_identificacion)
        except Exception as e:
            error_details = traceback.format_exc()
            messagebox.showerror("Error", f"Error al abrir los detalles del estudiante:\n{error_details}")

    def generar_pdf(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Sin selección", "Seleccione un estudiante para generar el PDF")
            return
        item = self.tree.item(selected[0])
        estudiante_data = item["values"]
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Paz y Salvo", ln=True, align="C")
        pdf.ln(10)
        campos = ["ID", "Identificación", "Nombre", "Apellido", "Curso"]
        for idx, campo in enumerate(campos):
            pdf.cell(50, 10, txt=f"{campo}:")
            pdf.cell(50, 10, txt=str(estudiante_data[idx]))
            pdf.ln(8)
        pdf.ln(10)
        pdf.cell(50, 10, txt="Fecha de emisión: " + datetime.date.today().strftime("%d/%m/%Y"))
        pdf_file = f"paz_y_salvo_estudiante_{estudiante_data[0]}.pdf"
        pdf.output(pdf_file)
        messagebox.showinfo("PDF generado", f"El PDF '{pdf_file}' ha sido generado correctamente.")

    def logout(self):
        confirm = messagebox.askyesno("Cerrar Sesión", "¿Está seguro de cerrar la sesión?")
        if confirm:
            self.root.destroy()
            from src.views.login_ui import LoginUI
            LoginUI(self.db).run()

    def run(self):
        self.refrescar_lista()
        self.root.mainloop()
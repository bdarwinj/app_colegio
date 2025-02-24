import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
from fpdf import FPDF
import datetime
import logging
from src.controllers.student_controller import StudentController
from src.controllers.enrollment_controller import EnrollmentController
from src.controllers.course_controller import CourseController
from src.controllers.config_controller import ConfigController
from src.controllers.user_controller import UserController
from src.controllers.payment_controller import PaymentController
from src.views.config_ui import ConfigUI
from src.views.user_management_ui import UserManagementUI
from src.views.payment_ui import PaymentUI
from src.views.login_ui import LoginUI
from src.views.student_details_window import StudentDetailsWindow
from src.views.enrollment_management_ui import EnrollmentManagementUI
from src.utils.export_students import export_students_to_excel, export_students_to_pdf

# Configuración de logging para registrar eventos y errores
logging.basicConfig(filename='app_ui.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Constantes para mensajes
MSG_ERROR = "Error"
MSG_SUCCESS = "Éxito"
MSG_FIELDS_INCOMPLETE = "Campos incompletos"
MSG_INVALID_VALUE = "Valor inválido"
MSG_SELECTION_REQUIRED = "Selección requerida"
MSG_CONFIRMATION = "¿Está seguro de cerrar la sesión?"

class ChangePasswordWindow(tk.Toplevel):
    def __init__(self, master, user_controller, current_user):
        super().__init__(master)
        self.user_controller = user_controller
        self.current_user = current_user
        self.title("Cambiar Clave")
        self.geometry("400x250")
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="20")
        frame.pack(expand=True, fill="both")
        
        ttk.Label(frame, text="Clave Actual:").grid(row=0, column=0, sticky="w", pady=5)
        self.old_password_entry = ttk.Entry(frame, show="*")
        self.old_password_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Nueva Clave:").grid(row=1, column=0, sticky="w", pady=5)
        self.new_password_entry = ttk.Entry(frame, show="*")
        self.new_password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Confirmar Nueva Clave:").grid(row=2, column=0, sticky="w", pady=5)
        self.confirm_password_entry = ttk.Entry(frame, show="*")
        self.confirm_password_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        self.change_password_button = ttk.Button(frame, text="Cambiar Clave", command=self.change_password)
        self.change_password_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        frame.columnconfigure(1, weight=1)

    def validate_inputs(self):
        old_password = self.old_password_entry.get().strip()
        new_password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        
        if not old_password or not new_password or not confirm_password:
            messagebox.showerror(MSG_ERROR, "Todos los campos son obligatorios.")
            return False
        if new_password != confirm_password:
            messagebox.showerror(MSG_ERROR, "La nueva clave y su confirmación no coinciden.")
            return False
        return True

    def change_password(self):
        if not self.validate_inputs():
            return
        
        old_password = self.old_password_entry.get().strip()
        new_password = self.new_password_entry.get().strip()
        
        try:
            success, message = self.user_controller.change_password(self.current_user, old_password, new_password)
            if success:
                messagebox.showinfo(MSG_SUCCESS, message)
                logging.info(f"Contraseña cambiada exitosamente para usuario: {self.current_user}")
                self.destroy()
            else:
                messagebox.showerror(MSG_ERROR, message)
                logging.warning(f"Intento fallido de cambio de contraseña para usuario: {self.current_user}")
        except Exception as e:
            logging.error(f"Error al cambiar la contraseña: {e}")
            messagebox.showerror(MSG_ERROR, f"Ocurrió un error al cambiar la clave: {str(e)}")

class AppUI:
    def __init__(self, db, user):
        self.db = db
        self.user = user
        self.student_controller = StudentController(self.db)
        self.course_controller = CourseController(self.db)
        self.config_controller = ConfigController(self.db)
        self.user_controller = UserController(self.db)
        self.payment_controller = PaymentController(self.db)
        self.root = tk.Tk()
        
        # Cargar configuración para el nombre de la escuela y el logo
        configs = self.config_controller.get_all_configs()
        self.school_name = configs.get("SCHOOL_NAME") or "School Name"
        self.logo_path = configs.get("LOGO_PATH") or ""
        self.abs_logo_path = os.path.abspath(self.logo_path)
        
        self.root.title(f"{self.school_name} - Sistema de Pagos (Usuario: {self.user.username})")
        self.root.geometry("900x650")
        self.create_widgets()

    def create_widgets(self):
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        if os.path.exists(self.abs_logo_path):
            try:
                from PIL import Image  # Asegurarse de importar Image
                image = Image.open(self.abs_logo_path)
                image = image.resize((80, 80), Image.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(image)
                logo_label = ttk.Label(header_frame, image=self.logo_image)
                logo_label.pack(side="left", padx=5)
            except Exception as e:
                logging.error(f"Error al cargar el logo: {e}")
        else:
            logging.warning(f"No se encontró la imagen en: {self.abs_logo_path}")
        
        name_label = ttk.Label(header_frame, text=self.root.title(), font=("Arial", 18, "bold"))
        name_label.pack(side="left", padx=10)
        
        btn_change_password = ttk.Button(header_frame, text="Cambiar Clave", command=self.open_change_password_window)
        btn_change_password.pack(side="right", padx=10)
        btn_logout = ttk.Button(header_frame, text="Cerrar Sesión", command=self.logout)
        btn_logout.pack(side="right", padx=10)

        if self.user.role == "admin":
            self.create_admin_panel()
            self.create_student_registration_frame()
        elif self.user.role == "user":
            self.btn_registrar_pago = ttk.Button(self.root, text="Registrar Pago", command=self.registrar_pago)
            self.btn_registrar_pago.pack(pady=5)

        self.create_students_list_frame()

        actions_frame = ttk.Frame(self.root)
        actions_frame.pack(pady=5)
        self.btn_refrescar = ttk.Button(actions_frame, text="Refrescar Lista", command=self.refrescar_lista)
        self.btn_refrescar.pack(side="left", padx=5)
        self.btn_pdf = ttk.Button(actions_frame, text="Generar Paz y Salvo", command=self.generar_pdf)
        self.btn_pdf.pack(side="left", padx=5)
        self.btn_export_excel = ttk.Button(actions_frame, text="Exportar a Excel", command=self.export_students_excel)
        self.btn_export_excel.pack(side="left", padx=5)
        self.btn_export_pdf = ttk.Button(actions_frame, text="Exportar a PDF", command=self.export_students_pdf)
        self.btn_export_pdf.pack(side="left", padx=5)
        
        # Botón adicional para gestionar inscripciones (para admin)
        if self.user.role == "admin":
            self.btn_manage_enrollments = ttk.Button(actions_frame, text="Gestionar Inscripciones", command=self.manage_enrollments)
            self.btn_manage_enrollments.pack(side="left", padx=5)

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

    def create_student_registration_frame(self):
        self.frame_form = ttk.LabelFrame(self.root, text="Registrar Estudiante")
        self.frame_form.pack(padx=10, pady=10, fill="x")
        labels = ["Número de Identificación", "Nombre", "Apellido", "Representante", "Teléfono"]
        self.entries = {}
        
        # Función de validación para que solo se acepten dígitos (o cadena vacía)
        def validate_numeric(P):
            return P.isdigit() or P == ""
        
        vcmd = (self.root.register(validate_numeric), '%P')
        
        # Al perder foco, obligar que el campo no quede vacío
        def on_focusout_numeric(event):
            if event.widget.get().strip() == "":
                messagebox.showwarning(MSG_FIELDS_INCOMPLETE, "Este campo es obligatorio y debe ser numérico.")
                event.widget.focus_set()
        
        for idx, text in enumerate(labels):
            ttk.Label(self.frame_form, text=f"{text}:").grid(row=idx, column=0, sticky="w", padx=5, pady=5)
            if text in ["Número de Identificación", "Teléfono"]:
                entry = ttk.Entry(self.frame_form, validate="key", validatecommand=vcmd)
                entry.bind("<FocusOut>", on_focusout_numeric)
            else:
                entry = ttk.Entry(self.frame_form)
            entry.grid(row=idx, column=1, padx=5, pady=5)
            self.entries[text] = entry

        ttk.Label(self.frame_form, text="Curso:").grid(row=len(labels), column=0, sticky="w", padx=5, pady=5)
        self.combo_course = ttk.Combobox(self.frame_form, state="readonly")
        self.combo_course.grid(row=len(labels), column=1, padx=5, pady=5)
        self.load_courses_into_combobox()

        self.btn_registrar = ttk.Button(self.frame_form, text="Registrar Estudiante", command=self.registrar_estudiante)
        self.btn_registrar.grid(row=len(labels) + 1, column=0, columnspan=2, pady=10)

    def _create_label_entry(self, parent, text, row):
        ttk.Label(parent, text=f"{text}:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        entry = ttk.Entry(parent)
        entry.grid(row=row, column=1, padx=5, pady=5)
        self.entries[text] = entry

    def create_students_list_frame(self):
        self.frame_lista = ttk.LabelFrame(self.root, text="Lista de Estudiantes")
        self.frame_lista.pack(padx=10, pady=10, fill="both", expand=True)
        self.columns = ("id", "identificacion", "nombre", "apellido", "curso")
        self.tree = ttk.Treeview(self.frame_lista, columns=self.columns, show="headings")
        for col in self.columns:
            self.tree.heading(col, text=col.capitalize(), command=lambda _col=col: self.sort_by(_col))
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_student_double_click)

    def sort_by(self, col):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        try:
            data.sort(key=lambda t: float(t[0]))
        except ValueError:
            data.sort(key=lambda t: t[0])
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)

    def editar_configuracion(self):
        ConfigUI(self.db)

    def registrar_pago(self):
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
        ttk.Label(frame_form, text="Sección (opcional):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_course_section = ttk.Entry(frame_form)
        self.entry_course_section.grid(row=1, column=1, padx=5, pady=5)
        btn_add = ttk.Button(frame_form, text="Agregar", command=self.add_course)
        btn_add.grid(row=2, column=0, padx=5, pady=5)
        btn_edit = ttk.Button(frame_form, text="Editar", command=self.edit_course)
        btn_edit.grid(row=2, column=1, padx=5, pady=5)
        btn_deactivate = ttk.Button(frame_form, text="Desactivar", command=self.deactivate_course)
        btn_deactivate.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def manage_users(self):
        UserManagementUI(self.db)

    def load_courses_into_tree(self):
        for item in self.courses_tree.get_children():
            self.courses_tree.delete(item)
        courses = self.course_controller.get_all_courses()
        for course in courses:
            full_name = f"{course['name']} - {course['seccion']}" if course.get("seccion") and course["seccion"].strip() else course["name"]
            self.courses_tree.insert("", "end", values=(course["id"], full_name, "Sí" if course["active"] == 1 else "No"))
        self.load_courses_into_combobox()

    def add_course(self):
        name = self.entry_course_name.get().strip()
        section = self.entry_course_section.get().strip()  # Puede estar vacío
        if not name:
            messagebox.showwarning(MSG_FIELDS_INCOMPLETE, "Ingrese el nombre del curso.")
            return
        success, msg = self.course_controller.add_course(name, section)
        if success:
            messagebox.showinfo(MSG_SUCCESS, msg)
            self.load_courses_into_tree()
            self.entry_course_name.delete(0, tk.END)
            self.entry_course_section.delete(0, tk.END)
        else:
            messagebox.showerror(MSG_ERROR, msg)

    def edit_course(self):
        selected = self.courses_tree.selection()
        if not selected:
            messagebox.showwarning(MSG_SELECTION_REQUIRED, "Seleccione un curso para editar.")
            return
        course_item = self.courses_tree.item(selected[0])
        course_id = course_item["values"][0]
        new_name = self.entry_course_name.get().strip()
        new_section = self.entry_course_section.get().strip()  # Opcional
        if not new_name:
            messagebox.showwarning(MSG_FIELDS_INCOMPLETE, "Ingrese el nuevo nombre del curso.")
            return
        success, msg = self.course_controller.edit_course(course_id, new_name, new_section)
        if success:
            messagebox.showinfo(MSG_SUCCESS, msg)
            self.load_courses_into_tree()
            self.entry_course_name.delete(0, tk.END)
            self.entry_course_section.delete(0, tk.END)
        else:
            messagebox.showerror(MSG_ERROR, msg)

    def deactivate_course(self):
        selected = self.courses_tree.selection()
        if not selected:
            messagebox.showwarning(MSG_SELECTION_REQUIRED, "Seleccione un curso para desactivar.")
            return
        course_item = self.courses_tree.item(selected[0])
        course_id = course_item["values"][0]
        confirm = messagebox.askyesno("Confirmar", "¿Está seguro de desactivar el curso?")
        if confirm:
            success, msg = self.course_controller.deactivate_course(course_id)
            if success:
                messagebox.showinfo(MSG_SUCCESS, msg)
                self.load_courses_into_tree()
            else:
                messagebox.showerror(MSG_ERROR, msg)

    def load_courses_into_combobox(self):
        courses = self.course_controller.get_active_courses()
        course_names = []
        course_ids = []
        for course in courses:
            full_name = f"{course['name']} - {course['seccion']}" if course.get("seccion") and course["seccion"].strip() else course["name"]
            course_names.append(full_name)
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
            messagebox.showwarning(MSG_FIELDS_INCOMPLETE, "Por favor, llene todos los campos.")
            return
        course_id = self.course_map.get(course_name)
        success, msg = self.student_controller.register_student(
            identificacion, nombre, apellido, course_id, representante, telefono)
        if success:
            messagebox.showinfo(MSG_SUCCESS, msg)
            # Crear inscripción para el año académico actual
            student_record = self.student_controller.get_student_by_identification(identificacion)
            if student_record:
                student_id = student_record["id"]
                current_year = datetime.datetime.now().year
                enrollment_controller = EnrollmentController(self.db)
                enroll_success, enroll_msg, enrollment_id = enrollment_controller.create_enrollment(
                    student_id, course_id, current_year, status="inscrito"
                )
                if enroll_success:
                    logging.info(f"Inscripción creada correctamente para el estudiante {identificacion} (Enrollment ID: {enrollment_id}).")
                else:
                    logging.error(f"Error al crear inscripción para el estudiante {identificacion}: {enroll_msg}")
            else:
                logging.error("No se pudo recuperar el registro del estudiante recién creado.")
            self.limpiar_formulario()
            self.refrescar_lista()
        else:
            messagebox.showerror(MSG_ERROR, msg)

    def limpiar_formulario(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.combo_course.set("")

    def refrescar_lista(self):
        current_ids = {self.tree.item(item)['values'][0] for item in self.tree.get_children()}
        new_estudiantes = self.student_controller.get_all_students()
        new_ids = set()
        
        for est in new_estudiantes:
            new_ids.add(est['id'])
            if est['id'] not in current_ids:
                course_name = est.get("course_name", "N/A")
                self.tree.insert("", "end", values=(est["id"], est["identificacion"], est["nombre"], est["apellido"], course_name))
        
        # Eliminar elementos que ya no están
        for item in self.tree.get_children():
            if self.tree.item(item)['values'][0] not in new_ids:
                self.tree.delete(item)
        
        if not new_estudiantes:
            messagebox.showinfo("Información", "No se han encontrado estudiantes.")

    def on_student_double_click(self, event):
        try:
            selected = self.tree.selection()
            if selected:
                item = self.tree.item(selected[0])
                student_identificacion = item["values"][1]
                StudentDetailsWindow(self.db, student_identificacion)
        except Exception as e:
            logging.error(f"Error al abrir detalles del estudiante: {e}")
            messagebox.showerror(MSG_ERROR, f"Error al abrir los detalles del estudiante: {str(e)}")

    def generar_pdf(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(MSG_SELECTION_REQUIRED, "Seleccione un estudiante para generar el PDF")
            return

        item = self.tree.item(selected[0])
        estudiante_data = item["values"]

        pdf = FPDF()
        pdf.add_page()

        # Agregar logo del colegio si existe
        if os.path.exists(self.abs_logo_path):
            try:
                pdf.image(self.abs_logo_path, x=10, y=8, w=30)
            except Exception as e:
                logging.error(f"Error al insertar logo en PDF: {e}")
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, txt=self.school_name, ln=True, align="C")
        pdf.ln(5)
        pdf.cell(200, 10, txt="Paz y Salvo", ln=True, align="C")
        pdf.ln(10)

        # Mostrar datos del estudiante
        campos = ["ID", "Identificación", "Nombre", "Apellido", "Curso"]
        for idx, campo in enumerate(campos):
            pdf.set_font("Arial", "B", 12)
            pdf.cell(50, 10, txt=f"{campo}:")
            pdf.set_font("Arial", "", 12)
            pdf.cell(50, 10, txt=str(estudiante_data[idx]))
            pdf.ln(8)
        pdf.ln(10)

        # Usar PaymentController para obtener y sumar los pagos del estudiante
        student_id = estudiante_data[0]  # Se asume que el id del estudiante está en la posición 0.
        pagos = self.payment_controller.get_payments_by_student(student_id)
        total_pagado = sum(float(payment["amount"]) for payment in pagos if payment["amount"] is not None)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, txt="Total Pagado:")
        pdf.set_font("Arial", "", 12)
        formatted_total = f"{total_pagado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        pdf.cell(50, 10, txt=f"${formatted_total}")
        pdf.ln(10)

        # Agregar la fecha de emisión
        pdf.cell(50, 10, txt="Fecha de emisión: " + datetime.date.today().strftime("%d/%m/%Y"))

        default_filename = f"paz_y_salvo_{estudiante_data[2]}.pdf"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=default_filename,
            title="Guardar Paz y Salvo"
        )
        if file_path:
            pdf.output(file_path)
            messagebox.showinfo("PDF generado", f"El PDF '{file_path}' ha sido generado correctamente.")

    def _export_students(self, export_func, file_extension, file_type):
        try:
            estudiantes = self.student_controller.get_all_students()
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            default_filename = f"{self.school_name}_Listado_Estudiantes_{timestamp}{file_extension}"
            file_path = filedialog.asksaveasfilename(defaultextension=file_extension,
                                          filetypes=[(file_type, f"*{file_extension}")],
                                          initialfile=default_filename)
            if not file_path:
                return
            # Se pasa la instancia de course_controller como quinto argumento
            export_func(estudiantes, file_path, self.school_name, self.logo_path, self.course_controller)
            messagebox.showinfo("Exportación exitosa", f"Listado exportado a {file_type}: {file_path}")
        except Exception as e:
            logging.error(f"Error al exportar a {file_type}: {e}")
            messagebox.showerror(MSG_ERROR, f"Error al exportar a {file_type}: {str(e)}")

    def export_students_excel(self):
        self._export_students(export_students_to_excel, ".xlsx", "Excel")

    def export_students_pdf(self):
        self._export_students(export_students_to_pdf, ".pdf", "PDF")

    def logout(self):
        confirm = messagebox.askyesno("Cerrar Sesión", MSG_CONFIRMATION)
        if confirm:
            self.root.destroy()
            LoginUI(self.db).run()

    def open_change_password_window(self):
        ChangePasswordWindow(self.root, self.user_controller, self.user.username)

    def manage_enrollments(self):
        """
        Abre la interfaz de Gestión de Inscripciones.
        """
        from src.views.enrollment_management_ui import EnrollmentManagementUI
        EnrollmentManagementUI(self.db)

    def run(self):
        self.refrescar_lista()
        self.root.mainloop()
# src/views/dashboard_window.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime
from fpdf import FPDF
import os

class DashboardWindow(tk.Toplevel):
    def __init__(self, parent, db, student_controller, course_controller, payment_controller):
        """
        Ventana de Dashboard que muestra estadísticas del sistema:
         - Número de cursos totales
         - Número de cursos con alumnos
         - Número total de alumnos
         - Número de alumnos por curso
         - Total dinero recogido en el mes
         - Total dinero recogido en el año
         - Alumnos sin pago en el mes actual
        """
        super().__init__(parent)
        self.db = db  # Guardamos la conexión a la base de datos
        self.title("Dashboard - Estadísticas")
        self.geometry("600x500")
        
        self.student_controller = student_controller
        self.course_controller = course_controller
        self.payment_controller = payment_controller
        
        self.students_without_payment_this_month = []  # Lista para guardar alumnos sin pago
        self.create_widgets()
        self.load_stats()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(expand=True, fill="both")

        self.label_title = ttk.Label(self.main_frame, text="Dashboard de Estadísticas", font=("Arial", 16, "bold"))
        self.label_title.pack(pady=5)

        # Texto con la información de estadísticas
        self.stats_text = tk.Text(self.main_frame, height=15, width=70, state="disabled")
        self.stats_text.pack(pady=5, fill="both", expand=True)

        # Botón para exportar la lista de alumnos sin pago a PDF
        self.btn_export_pdf = ttk.Button(self.main_frame, text="Exportar Lista de Deudores a PDF", command=self.export_dashboard_pdf)
        self.btn_export_pdf.pack(pady=10)

    def load_stats(self):
        """
        Carga las estadísticas y las muestra en el Text widget.
        """
        self.stats_text.configure(state="normal")
        self.stats_text.delete("1.0", tk.END)

        # 1. Número de cursos totales
        all_courses = self.course_controller.get_all_courses()
        total_courses = len(all_courses)

        # 2. Número de cursos con alumnos
        all_students = self.student_controller.get_all_students()
        course_names_in_use = set(stu["course_name"] for stu in all_students if stu.get("course_name"))
        courses_with_students = len(course_names_in_use)

        # 3. Número total de alumnos
        total_students = len(all_students)

        # 4. Número de alumnos por curso
        course_count_map = {}
        for stu in all_students:
            c_name = stu.get("course_name", "N/A")
            course_count_map[c_name] = course_count_map.get(c_name, 0) + 1
        
        # 5. Dinero recogido en el mes actual
        current_month_str = datetime.datetime.now().strftime("%Y-%m")  # "YYYY-MM"
        payments_month = self.payment_controller.get_payments_in_month(current_month_str)
        total_month = sum(pay["amount"] for pay in payments_month if pay["amount"])

        # 6. Dinero recogido en el año actual
        current_year = datetime.datetime.now().year
        payments_year = self.payment_controller.get_payments_in_year(current_year)
        total_year = sum(pay["amount"] for pay in payments_year if pay["amount"])

        # 7. Alumnos sin pago en el mes actual
        student_ids_paid_this_month = set(pay["student_id"] for pay in payments_month)
        students_without_payment = [stu for stu in all_students if stu["id"] not in student_ids_paid_this_month]
        self.students_without_payment_this_month = students_without_payment

        # Construir el texto a mostrar
        info = []
        info.append(f"Número total de cursos: {total_courses}")
        info.append(f"Número de cursos con alumnos: {courses_with_students}")
        info.append(f"Número total de alumnos: {total_students}")
        
        info.append("\nAlumnos por curso:")
        for c_name, count in course_count_map.items():
            info.append(f"  - {c_name}: {count}")
        
        info.append(f"\nDinero recogido en el mes (fecha {current_month_str}): {total_month}")
        info.append(f"Dinero recogido en el año {current_year}: {total_year}")
        
        info.append(f"\nAlumnos sin pago en el mes actual: {len(students_without_payment)}")
        if len(students_without_payment) > 0:
            info.append("Lista de alumnos sin pago este mes:")
            for stu in students_without_payment:
                full_name = f"{stu['nombre']} {stu['apellido']}".strip()
                info.append(f"  - {stu['identificacion']} | {full_name}")
        
        final_text = "\n".join(info)
        self.stats_text.insert(tk.END, final_text)
        self.stats_text.configure(state="disabled")

    def export_dashboard_pdf(self):
        """
        Genera un PDF que incluye las estadísticas generales del dashboard y la lista de alumnos sin pago en el mes actual.
        El PDF incluye:
         - El logo y nombre del colegio.
         - El bloque de estadísticas (excluyendo la lista de alumnos sin pago).
         - Una tabla con la lista de alumnos sin pago en el mes actual (Identificación, Nombre, Apellido, Curso).
         - La fecha de generación al final.
        """
        from src.controllers.config_controller import ConfigController
        config_controller = ConfigController(self.db)
        configs = config_controller.get_all_configs()
        school_name = configs.get("SCHOOL_NAME", "Colegio Ejemplo")
        logo_path = configs.get("LOGO_PATH", "logo.png")
        
        pdf = FPDF()
        pdf.add_page()
        
        # Insertar logo si existe
        if os.path.exists(logo_path):
            try:
                pdf.image(logo_path, x=10, y=8, w=20)
            except Exception as e:
                print(f"Error al insertar logo en PDF: {e}")
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, school_name, ln=True, align="C")
        pdf.ln(5)
        
        # Título del reporte de Dashboard
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Dashboard de Estadísticas", ln=True, align="C")
        pdf.ln(5)
        
        # Obtener el contenido de stats_text y eliminar la lista de alumnos sin pago
        full_stats = self.stats_text.get("1.0", tk.END).strip()
        # Separamos por la línea "Lista de alumnos sin pago este mes:" y usamos solo la parte anterior
        stats_only = full_stats.split("Lista de alumnos sin pago este mes:")[0].strip()
        
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, stats_only)
        pdf.ln(5)
        
        # Separador para la tabla de deudores
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Lista de Alumnos sin Pago en el Mes Actual", ln=True, align="C")
        pdf.ln(5)
        
        # Encabezados de la tabla
        headers = ["Identificacion", "Nombre", "Apellido", "Curso"]
        pdf.set_font("Arial", "B", 11)
        col_widths = [40, 40, 40, 50]  # Ajustar según necesidad
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, border=1, align="C")
        pdf.ln()
        
        pdf.set_font("Arial", "", 12)
        for stu in self.students_without_payment_this_month:
            ident = stu.get("identificacion", "")
            nombre = stu.get("nombre", "")
            apellido = stu.get("apellido", "")
            curso = stu.get("course_name", "N/A")
            row_data = [ident, nombre, apellido, curso]
            for i, data in enumerate(row_data):
                pdf.cell(col_widths[i], 10, str(data), border=1, align="C")
            pdf.ln()
        
        pdf.ln(10)
        generation_date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, f"Generado el {generation_date}", ln=True, align="R")
        
        default_filename = "Dashboard_Estadisticas.pdf"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=default_filename,
            title="Guardar PDF de Dashboard",
            filetypes=[("PDF files", "*.pdf")]
        )
        if file_path:
            pdf.output(file_path)
            messagebox.showinfo("Éxito", f"PDF guardado exitosamente: {file_path}")


import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime
from fpdf import FPDF
import os

class PDFWithHeaderFooter(FPDF):
    def __init__(self, logo_path, school_name):
        super().__init__()
        self.logo_path = logo_path
        self.school_name = school_name

    def header(self):
        # Insertar el logo
        if os.path.exists(self.logo_path):
            try:
                self.image(self.logo_path, x=10, y=8, w=25)  # Logo a la izquierda
            except Exception as e:
                print(f"Error al insertar logo: {e}")
        
        # Colocar el nombre del colegio al lado del logo
        self.set_xy(10, 8)  # X=40 para dejar espacio al logo, Y=8 para alinearlo
        self.set_font("Arial", "B", 18)  # Fuente en negrita, tamaño 18
        self.set_text_color(0, 51, 102)  # Color azul oscuro
        self.cell(0, 10, self.school_name, ln=True, align="C")  # Escribir el nombre
        
        # Título del reporte debajo
        self.set_xy(10, 20)  # Posición debajo del logo y nombre
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Dashboard de Estadísticas", ln=True, align="C")
        
        # Fecha de generación
        self.set_font("Arial", "I", 10)
        self.set_text_color(100, 100, 100)  # Color gris
        self.cell(0, 5, f"Generado el {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align="C")
        
        # Línea decorativa
        self.set_line_width(0.5)
        self.set_draw_color(0, 51, 102)  # Azul oscuro
        self.line(10, 35, self.w - 10, 35)  # Línea horizontal
        self.ln(10)  # Espacio adicional

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(150, 150, 150)  # Gris claro
        self.cell(0, 10, f"Página {self.page_no()} - Reporte generado por Sistema Escolar", 0, 0, "C")

class DashboardWindow(tk.Toplevel):
    def __init__(self, parent, db, student_controller, course_controller, payment_controller):
        super().__init__(parent)
        self.db = db
        self.title("Dashboard - Estadísticas")
        self.geometry("600x500")
        self.student_controller = student_controller
        self.course_controller = course_controller
        self.payment_controller = payment_controller
        self.students_without_payment_this_month = []
        self.create_widgets()
        self.load_stats()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(expand=True, fill="both")
        self.label_title = ttk.Label(self.main_frame, text="Dashboard de Estadísticas", font=("Arial", 16, "bold"))
        self.label_title.pack(pady=5)
        self.stats_text = tk.Text(self.main_frame, height=15, width=70, state="disabled")
        self.stats_text.pack(pady=5, fill="both", expand=True)
        self.btn_export_pdf = ttk.Button(self.main_frame, text="Exportar Lista de Deudores a PDF", command=self.export_dashboard_pdf)
        self.btn_export_pdf.pack(pady=10)

    def load_stats(self):
        self.stats_text.configure(state="normal")
        self.stats_text.delete("1.0", tk.END)
        all_courses = self.course_controller.get_all_courses()
        all_students = self.student_controller.get_all_students()
        total_courses = len(all_courses)
        total_students = len(all_students)
        course_names_in_use = {stu["course_name"] for stu in all_students if stu.get("course_name")}
        courses_with_students = len(course_names_in_use)
        course_count_map = {c_name: sum(1 for stu in all_students if stu.get("course_name") == c_name) for c_name in course_names_in_use}
        now = datetime.datetime.now()
        current_month_str = now.strftime("%Y-%m")
        current_year = now.year
        payments_month = self.payment_controller.get_payments_in_month(current_month_str)
        total_month = sum(pay["amount"] for pay in payments_month if pay["amount"])
        payments_year = self.payment_controller.get_payments_in_year(current_year)
        total_year = sum(pay["amount"] for pay in payments_year if pay["amount"])
        student_ids_paid_this_month = {pay["student_id"] for pay in payments_month}
        self.students_without_payment_this_month = [stu for stu in all_students if stu["id"] not in student_ids_paid_this_month]
        info = (
            f"Número total de cursos: {total_courses}\n"
            f"Número de cursos con alumnos: {courses_with_students}\n"
            f"Número total de alumnos: {total_students}\n\n"
            "Alumnos por curso:\n" + "\n".join(f"  - {c_name}: {count}" for c_name, count in course_count_map.items()) + "\n\n"
            f"Dinero recogido en el mes ({current_month_str}): {total_month}\n"
            f"Dinero recogido en el año {current_year}: {total_year}\n\n"
            f"Alumnos sin pago en el mes actual: {len(self.students_without_payment_this_month)}\n"
        )
        if self.students_without_payment_this_month:
            info += "Lista de alumnos sin pago este mes:\n" + "\n".join(
                f"  - {stu['identificacion']} | {stu['nombre']} {stu['apellido']}" for stu in self.students_without_payment_this_month
            )
        self.stats_text.insert(tk.END, info)
        self.stats_text.configure(state="disabled")

    def export_dashboard_pdf(self):
        from src.controllers.config_controller import ConfigController
        config_controller = ConfigController(self.db)
        configs = config_controller.get_all_configs()
        school_name = configs.get("SCHOOL_NAME", "Colegio Ejemplo")
        logo_path = configs.get("LOGO_PATH", "logo.png")
        
        pdf = PDFWithHeaderFooter(logo_path, school_name)
        pdf.set_margins(left=15, top=40, right=15)  # Márgenes más amplios
        pdf.add_page()
        
        # Sección de estadísticas
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(0, 51, 102)  # Azul oscuro
        pdf.cell(0, 10, "Estadísticas Generales", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(0, 0, 0)  # Negro
        full_stats = self.stats_text.get("1.0", tk.END).strip().split("Lista de alumnos sin pago este mes:")[0].strip()
        pdf.multi_cell(0, 6, full_stats)
        pdf.ln(10)
        
        # Sección de deudores
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, "Lista de Alumnos sin Pago en el Mes Actual", ln=True)
        pdf.ln(5)
        
        headers = ["Identificación", "Nombre", "Apellido", "Curso"]
        table_data = [[stu.get("identificacion", ""), stu.get("nombre", ""), stu.get("apellido", ""), stu.get("course_name", "N/A")]
                      for stu in self.students_without_payment_this_month]
        
        # Calcular anchos de columnas
        col_widths = [max(pdf.get_string_width(str(row[i])) for row in table_data + [headers]) + 8 for i in range(len(headers))]
        total_width = sum(col_widths)
        if total_width > pdf.w - 30:
            scale_factor = (pdf.w - 30) / total_width
            col_widths = [w * scale_factor for w in col_widths]
        
        # Encabezados de la tabla
        pdf.set_fill_color(0, 102, 204)  # Azul claro
        pdf.set_text_color(255, 255, 255)  # Blanco
        pdf.set_font("Arial", "B", 10)
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, border=1, align="C", fill=True)
        pdf.ln()
        
        # Filas de la tabla
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(0, 0, 0)
        fill = False
        for row in table_data:
            pdf.set_fill_color(240, 245, 255) if fill else pdf.set_fill_color(255, 255, 255)  # Azul muy claro / Blanco
            for i, data in enumerate(row):
                pdf.cell(col_widths[i], 8, str(data), border=1, align="C", fill=True)
            pdf.ln()
            fill = not fill
        
        # Guardar el PDF
        default_filename = "Dashboard_Estadisticas.pdf"
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=default_filename, title="Guardar PDF", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            pdf.output(file_path)
            messagebox.showinfo("Éxito", f"PDF guardado exitosamente: {file_path}")
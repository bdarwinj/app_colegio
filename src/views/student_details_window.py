import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from fpdf import FPDF
import datetime
import traceback
import os
import locale
from src.controllers.student_controller import StudentController
from src.controllers.payment_controller import PaymentController
from src.controllers.config_controller import ConfigController  # To retrieve school settings from the DB
from config import SCHOOL_NAME as DEFAULT_SCHOOL_NAME, LOGO_PATH as DEFAULT_LOGO_PATH

class StudentDetailsWindow(tk.Toplevel):
    def __init__(self, db, student_identificacion):
        super().__init__()
        self.db = db
        self.student_identificacion = student_identificacion
        self.student_controller = StudentController(db)
        self.payment_controller = PaymentController(db)
        self.config_controller = ConfigController(db)
        self.title("Detalles del Estudiante")
        self.geometry("700x550")
        self.create_widgets()
        self.load_student_details()

    def create_widgets(self):
        self.frame_details = ttk.Frame(self, padding=10)
        self.frame_details.pack(fill="both", expand=True)
        
        # Título de la ventana
        self.label_info = ttk.Label(self.frame_details, text="Información del Estudiante", font=("Arial", 16, "bold"))
        self.label_info.pack(pady=5)

        self.details_text = tk.Text(self.frame_details, height=7, width=80, state="disabled", font=("Arial", 12))
        self.details_text.pack(pady=5)
        
        # Botones para acciones
        self.buttons_frame = ttk.Frame(self.frame_details)
        self.buttons_frame.pack(pady=10)

        self.btn_deactivate = ttk.Button(self.buttons_frame, text="Desactivar Estudiante", command=self.deactivate_student)
        self.btn_deactivate.grid(row=0, column=0, padx=5)

        self.btn_delete = ttk.Button(self.buttons_frame, text="Eliminar Estudiante", command=self.delete_student)
        self.btn_delete.grid(row=0, column=1, padx=5)

        self.btn_export_pdf = ttk.Button(self.buttons_frame, text="Exportar a PDF", command=self.export_pdf)
        self.btn_export_pdf.grid(row=0, column=2, padx=5)
        
        # Etiqueta para el historial de pagos
        self.label_history = ttk.Label(self.frame_details, text="Historial de Pagos", font=("Arial", 14, "bold"))
        self.label_history.pack(pady=5)
        
        # Creando la tabla para mostrar los pagos
        columns = ("receipt", "amount", "date", "description")
        self.tree_payments = ttk.Treeview(self.frame_details, columns=columns, show="headings", height=8)
        self.tree_payments.heading("receipt", text="Nº Recibo")
        self.tree_payments.heading("amount", text="Monto")
        self.tree_payments.heading("date", text="Fecha de Pago")
        self.tree_payments.heading("description", text="Descripción")
        
        self.tree_payments.column("receipt", width=80, anchor="center")
        self.tree_payments.column("amount", width=100, anchor="e")
        self.tree_payments.column("date", width=150, anchor="center")
        self.tree_payments.column("description", width=300, anchor="w")
        
        self.tree_payments.pack(pady=5, fill="x")
        self.tree_payments.bind("<Double-1>", self.on_payment_double_click)
        
    def load_student_details(self):
        try:
            student_row = self.student_controller.get_student_by_identification(self.student_identificacion)
            if not student_row:
                messagebox.showerror("Error", "No se encontró el estudiante.")
                self.destroy()
                return

            student = dict(student_row)
            # Formatear primera letra de nombre, apellido y representante en mayúscula
            nombre = student.get('nombre', '').capitalize()
            apellido = student.get('apellido', '').capitalize()
            representante = student.get('representante', '')
            if representante:
                representante = representante.capitalize()

            info = (
                f"ID: {student.get('id', '')}\n"
                f"Identificación: {student.get('identificacion', '')}\n"
                f"Nombre: {nombre}\n"
                f"Apellido: {apellido}\n"
                f"Curso: {student.get('course_name', '')}\n"
                f"Representante: {representante}\n"
                f"Teléfono: {student.get('telefono', '')}\n"
                f"Estado: {'Activo' if student.get('active', 1) == 1 else 'Desactivado'}\n"
            )
            
            self.details_text.configure(state="normal")
            self.details_text.delete("1.0", tk.END)
            self.details_text.insert(tk.END, info)
            self.details_text.configure(state="disabled")
            
            # Cargar y mostrar el historial de pagos en la tabla
            for row in self.tree_payments.get_children():
                self.tree_payments.delete(row)
            
            history_rows = self.payment_controller.get_payments_by_student(student.get("id"))
            if history_rows:
                for payment_row in history_rows:
                    payment = dict(payment_row)
                    self.tree_payments.insert("", tk.END, values=(
                        payment.get("receipt_number", ""),
                        payment.get("amount", ""),
                        payment.get("payment_date", ""),
                        payment.get("description", "")
                    ))
            else:
                self.tree_payments.insert("", tk.END, values=("No hay registros", "", "", ""))
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al cargar los detalles del estudiante: {e}")

    def on_payment_double_click(self, event):
        try:
            selected_item = self.tree_payments.selection()
            if not selected_item:
                return
            values = self.tree_payments.item(selected_item, "values")
            # Verificar si hay un registro válido (evitar el mensaje "No hay registros")
            if values[0] == "No hay registros":
                return
            
            # Extraer datos del pago seleccionado
            receipt_number, amount, payment_date, description = values

            # Obtener datos del colegio desde la configuración
            configs = self.config_controller.get_all_configs()
            school_name = configs.get("SCHOOL_NAME", DEFAULT_SCHOOL_NAME).title()
            logo_path = configs.get("LOGO_PATH", DEFAULT_LOGO_PATH)
            
            # Formatear el monto con coma como separador de miles y punto decimal
            try:
                formatted_amount = f"{float(amount):,.2f}"
            except Exception:
                formatted_amount = amount

            # Generar PDF del recibo de pago
            pdf = FPDF()
            pdf.add_page()
            
            add_pdf_header(pdf, logo_path, school_name, f"Recibo de Pago Nº {receipt_number}")

            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Monto: {formatted_amount}", ln=True)
            pdf.cell(0, 10, f"Fecha de Pago: {payment_date}", ln=True)
            pdf.multi_cell(0, 10, f"Descripción: {description}")
            
            # Permitir guardar el PDF
            default_filename = f"recibo_{receipt_number}.pdf"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                initialfile=default_filename,
                title="Guardar Recibo de Pago",
                filetypes=[("PDF files", "*.pdf")]
            )
            if file_path:
                pdf.output(file_path)
                messagebox.showinfo("Éxito", f"Recibo guardado exitosamente: {file_path}")
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al generar el recibo de pago: {e}")

    def deactivate_student(self):
        try:
            confirm = messagebox.askyesno("Confirmar", "¿Está seguro de desactivar este estudiante?")
            if not confirm:
                return
            success, msg = self.student_controller.deactivate_student(self.student_identificacion)
            if success:
                messagebox.showinfo("Éxito", "Estudiante desactivado correctamente.")
                self.load_student_details()
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al desactivar el estudiante: {e}")

    def delete_student(self):
        try:
            confirm = messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este estudiante?")
            if not confirm:
                return
            success, msg = self.student_controller.delete_student(self.student_identificacion)
            if success:
                messagebox.showinfo("Éxito", "Estudiante eliminado correctamente.")
                self.destroy()
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al eliminar el estudiante: {e}")

    def export_pdf(self):
        try:
            # Establecer la configuración regional a español para las fechas
            try:
                locale.setlocale(locale.LC_TIME, "es_ES.utf8")
            except Exception:
                pass

            # Obtener configuraciones de colegio
            configs = self.config_controller.get_all_configs()
            school_name = configs.get("SCHOOL_NAME", DEFAULT_SCHOOL_NAME).title()
            logo_path = configs.get("LOGO_PATH", DEFAULT_LOGO_PATH)
            
            pdf = FPDF()
            pdf.add_page()
            
            add_pdf_header(pdf, logo_path, school_name)

            student_row = self.student_controller.get_student_by_identification(self.student_identificacion)
            if not student_row:
                messagebox.showerror("Error", "No se encontró el estudiante.")
                return
            
            student = dict(student_row)
            nombre = student.get('nombre', '').capitalize()
            apellido = student.get('apellido', '').capitalize()
            representante = student.get('representante', '')
            if representante:
                representante = representante.capitalize()
            
            # Tabla con Datos del Estudiante con todos los bordes y encabezados
            pdf.set_font("Arial", "B", 12)
            cell_width1, cell_width2 = 50, 130
            pdf.cell(cell_width1, 10, "Campo", border=1, align="C")
            pdf.cell(cell_width2, 10, "Valor", border=1, align="C", ln=True)
            
            pdf.set_font("Arial", "", 12)
            datos = [
                ("Identificación", student.get('identificacion', '')),
                ("Nombre", nombre),
                ("Apellido", apellido),
                ("Curso", student.get('course_name', '')),
                ("Representante", representante),
                ("Teléfono", student.get('telefono', '')),
                ("Estado", "Activo" if student.get('active', 1) == 1 else "Desactivado")
            ]
            for campo, valor in datos:
                pdf.cell(cell_width1, 10, campo, border=1)
                pdf.cell(cell_width2, 10, str(valor), border=1, ln=True)
            
            pdf.ln(10)
            
            # Tabla del Historial de Pagos con bordes y encabezados
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Historial de Pagos", ln=True)
            pdf.ln(5)
            
            pdf.set_font("Arial", "B", 12)
            col_widths = [30, 30, 40, 70]
            headers = ["Nº Recibo", "Monto", "Fecha de Pago", "Descripción"]
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 10, header, border=1, align="C")
            pdf.ln()
            
            pdf.set_font("Arial", "", 12)
            history_rows = self.payment_controller.get_payments_by_student(student.get("id"))
            if history_rows:
                for payment_row in history_rows:
                    payment = dict(payment_row)
                    row_data = [
                        str(payment.get("receipt_number", "")),
                        str(payment.get("amount", "")),
                        str(payment.get("payment_date", "")),
                        str(payment.get("description", ""))
                    ]
                    for i, data in enumerate(row_data):
                        pdf.cell(col_widths[i], 10, data, border=1)
                    pdf.ln()
            else:
                pdf.cell(sum(col_widths), 10, "No se han encontrado pagos.", border=1, ln=True)
            
            pdf.ln(10)
            pdf.set_font("Arial", "", 10)
            emission_date = datetime.datetime.now().strftime("%d de %B de %Y")
            pdf.cell(0, 10, f"Generado el {emission_date}", ln=True, align="R")
            
            default_filename = f"{student.get('identificacion','')}_{student.get('nombre','')}_{student.get('apellido','')}.pdf"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                initialfile=default_filename,
                title="Guardar Información del Estudiante",
                filetypes=[("PDF files", "*.pdf")]
            )
            if file_path:
                pdf.output(file_path)
                messagebox.showinfo("Éxito", f"PDF exportado exitosamente: {file_path}")
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al exportar a PDF: {e}")

def add_pdf_header(pdf, logo_path=DEFAULT_LOGO_PATH, school_name=DEFAULT_SCHOOL_NAME, header_title="Detalles del Estudiante"):
    """
    Agrega el encabezado al PDF con el logo, el nombre del colegio y un título.
    """
    if logo_path and os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=10, y=8, w=30)
            pdf.ln(5) 
        except Exception as e:
            print("Error al cargar el logo en el PDF:", e)
    else:
        print("Logo no encontrado o ruta vacía:", logo_path)
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, school_name, ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, header_title, ln=True)
    pdf.ln(5)
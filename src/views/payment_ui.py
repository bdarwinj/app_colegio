import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from fpdf import FPDF
from src.controllers.payment_controller import PaymentController
from src.controllers.student_controller import StudentController
from src.controllers.config_controller import ConfigController
from config import SCHOOL_NAME as DEFAULT_SCHOOL_NAME, LOGO_PATH as DEFAULT_LOGO_PATH
import datetime
import traceback
import logging
from src.views.pdf_common import add_pdf_header  # Función común para encabezados PDF
from src.utils.pdf_utils import PDFWithHeaderFooter  # Clase PDF con encabezado y pie de página

# Configure logging
logging.basicConfig(filename='payment_ui.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Constants for messages
MSG_ERROR = "Error"
MSG_SUCCESS = "Éxito"
MSG_FIELDS_INCOMPLETE = "Campos incompletos"
MSG_INVALID_VALUE = "Valor inválido"
MSG_SELECTION_REQUIRED = "Selección requerida"
MSG_CONFIRMATION = "¿Está seguro de registrar este pago?"

class PaymentUI:
    def __init__(self, db):
        self.db = db
        self.payment_controller = PaymentController(db)
        self.student_controller = StudentController(db)
        self.config_controller = ConfigController(db)
        
        self.selected_student = None
        self.window = tk.Toplevel()
        self.window.title("Registrar Pago")
        self.window.geometry("600x400")
        
        # Cache all students for efficient searching
        self.all_students = self.student_controller.get_all_students()
        
        self.create_widgets()

    def create_widgets(self):
        """Crea y organiza los widgets de la interfaz de registro de pago."""
        # Frame para la búsqueda de alumnos
        search_frame = ttk.LabelFrame(self.window, text="Buscar Alumno")
        search_frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(search_frame, text="Ingrese identificación, nombre o apellido:")\
            .pack(anchor="w", padx=5, pady=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(fill="x", padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Listbox para mostrar resultados de búsqueda
        self.results_listbox = tk.Listbox(search_frame, height=8)
        self.results_listbox.pack(fill="both", padx=5, pady=5)
        self.results_listbox.bind("<<ListboxSelect>>", self.on_student_select)
        
        # Frame para mostrar detalles del pago
        details_frame = ttk.LabelFrame(self.window, text="Detalles del Pago")
        details_frame.pack(padx=10, pady=10, fill="x")
        
        # Campo para alumno seleccionado (read-only)
        ttk.Label(details_frame, text="Alumno Seleccionado:")\
            .grid(row=0, column=0, sticky="w", pady=5)
        self.selected_student_var = tk.StringVar()
        self.selected_student_entry = ttk.Entry(details_frame, textvariable=self.selected_student_var,
                                                state="readonly", width=45)
        self.selected_student_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Campo para monto del pago
        ttk.Label(details_frame, text="Monto:")\
            .grid(row=1, column=0, sticky="w", pady=5)
        self.entry_amount = ttk.Entry(details_frame, width=45)
        self.entry_amount.grid(row=1, column=1, pady=5, padx=5)
        
        # Campo para descripción del pago
        ttk.Label(details_frame, text="Descripción:")\
            .grid(row=2, column=0, sticky="w", pady=5)
        self.entry_description = ttk.Entry(details_frame, width=45)
        self.entry_description.grid(row=2, column=1, pady=5, padx=5)
        
        # Botón para registrar el pago
        btn_register = ttk.Button(self.window, text="Registrar Pago", command=self.register_payment)
        btn_register.pack(pady=10)
        
        # Bind de la tecla Enter para registrar pago
        self.window.bind('<Return>', lambda event: self.register_payment())
        
        # Inicialmente se pobla el listbox con todos los estudiantes
        self.populate_students_listbox(self.all_students)

    def on_search(self, event):
        """Filtra la lista de alumnos según la consulta ingresada."""
        query = self.search_var.get().lower().strip()
        try:
            if query:
                filtered_students = [
                    student for student in self.all_students
                    if query in str(student["identificacion"]).lower() or 
                       query in student["nombre"].lower() or 
                       query in student["apellido"].lower()
                ]
            else:
                filtered_students = self.all_students
            self.populate_students_listbox(filtered_students)
        except Exception as e:
            logging.error(f"Error searching students: {e}")
            messagebox.showerror(MSG_ERROR, f"Error al buscar alumnos: {e}")

    def populate_students_listbox(self, students):
        """Actualiza el listbox con los estudiantes filtrados."""
        self.results_listbox.delete(0, tk.END)
        self.students_data = []  # Mapeo entre índices y datos del alumno
        for student in students:
            full_name = f"{student['identificacion']} - {student['nombre']} {student['apellido']}"
            self.results_listbox.insert(tk.END, full_name.title())
            self.students_data.append(student)

    def on_student_select(self, event):
        """Actualiza el campo de alumno seleccionado según la elección en el listbox."""
        try:
            selection = self.results_listbox.curselection()
            if selection:
                index = selection[0]
                self.selected_student = self.students_data[index]
                display_text = f"{self.selected_student['identificacion']} - {self.selected_student['nombre']} {self.selected_student['apellido']}"
                self.selected_student_var.set(display_text.title())
            else:
                self.selected_student = None
                self.selected_student_var.set("")
        except Exception as e:
            logging.error(f"Error selecting student: {e}")
            messagebox.showerror(MSG_ERROR, f"Error al seleccionar alumno: {e}")

    def format_receipt_number(self, receipt_number, payment_date):
        """
        Formatea el número de recibo para incluir la fecha en formato YYYYMMDD y el número con 4 dígitos.
        Ejemplo: "20250303-0005"
        """
        try:
            dt = datetime.datetime.strptime(payment_date, "%Y-%m-%d %H:%M:%S")
            date_part = dt.strftime("%Y%m%d")
            formatted_number = f"{date_part}-{int(receipt_number):04d}"
            return formatted_number
        except Exception as e:
            logging.error(f"Error formatting receipt number: {e}")
            return str(receipt_number)

    def register_payment(self):
        """
        Registra el pago del alumno seleccionado, genera un PDF con el recibo y muestra el resultado.
        """
        if not self.selected_student:
            messagebox.showwarning(MSG_SELECTION_REQUIRED, "Seleccione un alumno.")
            return
        
        amount_text = self.entry_amount.get().strip()
        if not amount_text:
            messagebox.showwarning(MSG_FIELDS_INCOMPLETE, "Ingrese el monto.")
            return
        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError("El monto debe ser positivo.")
        except ValueError as ve:
            messagebox.showwarning(MSG_INVALID_VALUE, str(ve))
            return
        
        description = self.entry_description.get().strip()
        if not description:
            messagebox.showwarning(MSG_FIELDS_INCOMPLETE, "Ingrese una descripción.")
            return
        
        # Confirmación de pago
        if not messagebox.askyesno("Confirmar", MSG_CONFIRMATION):
            return
        
        try:
            success, msg, receipt_number, payment_date = self.payment_controller.register_payment(
                self.selected_student["id"], amount, description
            )
            if success:
                formatted_student_name = f"{self.selected_student['nombre']} {self.selected_student['apellido']}".title()
                formatted_receipt = self.format_receipt_number(receipt_number, payment_date)
                configs = self.config_controller.get_all_configs()

                pdf = PDFWithHeaderFooter(school_name=configs.get("SCHOOL_NAME", DEFAULT_SCHOOL_NAME), 
                                        logo_path=configs.get("LOGO_PATH", DEFAULT_LOGO_PATH), 
                                        receipt_number=formatted_receipt, titulo="Recibo de Pago Nº")
                pdf.add_page()                
                # Detalles del pago
                pdf.set_font("Arial", "B", 12)
                pdf.set_text_color(0, 51, 102)  # Azul oscuro
                pdf.cell(0, 10, "Detalles del Pago", ln=True)
                pdf.set_font("Arial", "", 10)
                pdf.set_text_color(0, 0, 0)  # Negro
                
                # Fondo gris claro para los detalles
                pdf.set_fill_color(240, 240, 240)  # Gris claro
                details = [
                    ("Recibo Nº", formatted_receipt),
                    ("Fecha y Hora", payment_date),
                    ("Alumno", formatted_student_name),
                    ("Monto", "{:,.2f}".format(amount).replace(",", "X").replace(".", ",").replace("X", ".")),
                    ("Descripción", description)
                ]
                for label, value in details:
                    pdf.cell(50, 8, label, border=1, align="L", fill=True)
                    pdf.cell(130, 8, value, border=1, align="L", ln=True, fill=True)
                
                default_filename = f"recibo_{formatted_receipt}_{formatted_student_name.replace(' ', '_')}.pdf"
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    initialfile=default_filename,
                    title="Guardar Recibo de Pago",
                    filetypes=[("PDF files", "*.pdf")]
                )
                if file_path:
                    pdf.output(file_path)
                    messagebox.showinfo(MSG_SUCCESS, f"Pago registrado exitosamente.\nRecibo Nº: {formatted_receipt}\nPDF generado: {file_path}")
                    logging.info(f"Payment registered: Receipt {formatted_receipt}, Student: {formatted_student_name}, Amount: {amount}")
                    self.window.destroy()
            else:
                messagebox.showerror(MSG_ERROR, msg)
                logging.warning(f"Failed payment attempt: {msg}")
        except Exception as e:
            logging.error(f"Error registering payment: {e}")
            messagebox.showerror(MSG_ERROR, f"Error al registrar pago: {e}")
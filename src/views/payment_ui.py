import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from fpdf import FPDF
from src.controllers.payment_controller import PaymentController
from src.controllers.student_controller import StudentController
from src.controllers.config_controller import ConfigController  # To retrieve school settings from the DB
from config import SCHOOL_NAME as DEFAULT_SCHOOL_NAME, LOGO_PATH as DEFAULT_LOGO_PATH
import datetime

class PaymentUI:
    def __init__(self, db):
        self.db = db
        self.payment_controller = PaymentController(db)
        self.student_controller = StudentController(db)
        # Create a ConfigController to fetch configuration values from the database.
        self.config_controller = ConfigController(db)
        
        self.window = tk.Toplevel()
        self.window.title("Registrar Pago")
        self.window.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.window, padding=10)
        frame.pack(expand=True, fill="both")

        # Combobox for selecting a student.
        ttk.Label(frame, text="Alumno:").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_student = ttk.Combobox(frame, state="readonly", width=30)
        self.combo_student.grid(row=0, column=1, pady=5)
        self.load_students()

        # Entry for payment amount.
        ttk.Label(frame, text="Monto:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_amount = ttk.Entry(frame, width=30)
        self.entry_amount.grid(row=1, column=1, pady=5)

        # Entry for an optional payment description.
        ttk.Label(frame, text="Descripción:").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_description = ttk.Entry(frame, width=30)
        self.entry_description.grid(row=2, column=1, pady=5)

        btn_register = ttk.Button(frame, text="Registrar Pago", command=self.register_payment)
        btn_register.grid(row=3, column=0, columnspan=2, pady=10)

    def load_students(self):
        """
        Loads all students from the database and populates the combobox.
        Assumes student_controller.get_all_students() returns a list of dictionaries 
        with keys: "id", "nombre", "apellido".
        """
        students = self.student_controller.get_all_students()
        self.students_map = {}
        student_names = []
        for student in students:
            # Capitalize the first letter of the first name and surname.
            full_name = f"{student['nombre']} {student['apellido']}"
            name = full_name.title()  # Title-case each word
            student_names.append(name)
            self.students_map[name] = student["id"]
        self.combo_student["values"] = student_names

    def register_payment(self):
        student_name = self.combo_student.get()
        if not student_name:
            messagebox.showwarning("Selección requerida", "Seleccione un estudiante.")
            return
        student_id = self.students_map[student_name]
        amount_text = self.entry_amount.get()
        if not amount_text:
            messagebox.showwarning("Campos incompletos", "Ingrese el monto.")
            return
        try:
            amount = float(amount_text)
        except ValueError:
            messagebox.showwarning("Valor inválido", "El monto debe ser numérico.")
            return
        description = self.entry_description.get()

        success, msg, receipt_number, payment_date = self.payment_controller.register_payment(
            student_id, amount, description
        )
        if success:
            # Ensure student name is in title case.
            formatted_student_name = student_name.title()
            self.generate_pdf(receipt_number, formatted_student_name, amount, description, payment_date)
            formatted_receipt = self.format_receipt_number(receipt_number, payment_date)
            messagebox.showinfo("Éxito", f"Pago registrado exitosamente.\nRecibo Nº: {formatted_receipt}")
            self.window.destroy()
        else:
            messagebox.showerror("Error", msg)

    def format_receipt_number(self, receipt_number, payment_date):
        """
        Format the receipt number to incorporate the payment date.
        For example, if payment_date is "2025-02-11 11:51:50" and receipt_number is 12,
        the formatted number would be "20250211-0012".
        """
        try:
            dt = datetime.datetime.strptime(payment_date, "%Y-%m-%d %H:%M:%S")
            date_part = dt.strftime("%Y%m%d")
            formatted_number = f"{date_part}-{int(receipt_number):04d}"
            return formatted_number
        except Exception as e:
            return f"{receipt_number}"

    def format_amount(self, amount):
        """
        Format the amount to separate thousands with dots and decimals with comma.
        E.g., 1234567.89 becomes "1.234.567,89"
        """
        # Format with US-style comma-thousands and period as decimal.
        formatted = "{:,.2f}".format(amount)
        # Swap comma and period.
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return formatted

    def generate_pdf(self, receipt_number, student_name, amount, description, payment_date):
        # Retrieve configuration from the database.
        configs = self.config_controller.get_all_configs()
        school_name = configs.get("SCHOOL_NAME", DEFAULT_SCHOOL_NAME)
        logo_path = configs.get("LOGO_PATH", DEFAULT_LOGO_PATH)

        pdf = FPDF()
        pdf.add_page()

        # Insert the logo if available.
        if logo_path:
            try:
                pdf.image(logo_path, x=10, y=8, w=30)
            except Exception as e:
                print("Error al cargar el logo en el PDF:", e)

        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, school_name, ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "Recibo de Pago", ln=True, align="C")
        pdf.ln(10)

        # Use the formatted receipt number and payment_date.
        formatted_receipt = self.format_receipt_number(receipt_number, payment_date)
        pdf.cell(0, 10, f"Recibo Nº: {formatted_receipt}", ln=True)
        pdf.cell(0, 10, f"Fecha y Hora: {payment_date}", ln=True)
        pdf.cell(0, 10, f"Alumno: {student_name}", ln=True)

        # Format the amount with thousands separator.
        formatted_amount = self.format_amount(amount)
        pdf.cell(0, 10, f"Monto: {formatted_amount}", ln=True)
        pdf.cell(0, 10, f"Descripción: {description}", ln=True)

        # Construct a default filename that includes the formatted receipt number and student's name.
        default_filename = f"recibo_{formatted_receipt}_{student_name.replace(' ', '_')}.pdf"
        # Open a file save dialog for the user to choose where to save the PDF.
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=default_filename,
            title="Guardar Recibo de Pago",
            filetypes=[("PDF files", "*.pdf")]
        )
        if file_path:
            pdf.output(file_path)
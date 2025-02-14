import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from fpdf import FPDF
from src.controllers.payment_controller import PaymentController
from src.controllers.student_controller import StudentController
from src.controllers.config_controller import ConfigController  # To retrieve school settings from the DB
from config import SCHOOL_NAME as DEFAULT_SCHOOL_NAME, LOGO_PATH as DEFAULT_LOGO_PATH
import datetime
import traceback

class PaymentUI:
    def __init__(self, db):
        self.db = db
        self.payment_controller = PaymentController(db)
        self.student_controller = StudentController(db)
        # Create a ConfigController to fetch configuration values from the database.
        self.config_controller = ConfigController(db)
        
        self.selected_student = None
        self.window = tk.Toplevel()
        self.window.title("Registrar Pago")
        self.window.geometry("600x400")
        self.create_widgets()

    def create_widgets(self):
        # Frame for student search functionality
        search_frame = ttk.LabelFrame(self.window, text="Buscar Alumno")
        search_frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(search_frame, text="Ingrese identificación, nombre o apellido:").pack(anchor="w", padx=5, pady=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(fill="x", padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Listbox to display search results
        self.results_listbox = tk.Listbox(search_frame, height=8)
        self.results_listbox.pack(fill="both", padx=5, pady=5)
        self.results_listbox.bind("<<ListboxSelect>>", self.on_student_select)
        
        # Frame for displaying selected student and payment details.
        details_frame = ttk.LabelFrame(self.window, text="Detalles del Pago")
        details_frame.pack(padx=10, pady=10, fill="x")
        
        # Selected student field (read only)
        ttk.Label(details_frame, text="Alumno Seleccionado:").grid(row=0, column=0, sticky="w", pady=5)
        self.selected_student_var = tk.StringVar()
        self.selected_student_entry = ttk.Entry(details_frame, textvariable=self.selected_student_var, state="readonly", width=45)
        self.selected_student_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Payment amount field.
        ttk.Label(details_frame, text="Monto:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_amount = ttk.Entry(details_frame, width=45)
        self.entry_amount.grid(row=1, column=1, pady=5, padx=5)
        
        # Payment description field.
        ttk.Label(details_frame, text="Descripción:").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_description = ttk.Entry(details_frame, width=45)
        self.entry_description.grid(row=2, column=1, pady=5, padx=5)
        
        btn_register = ttk.Button(self.window, text="Registrar Pago", command=self.register_payment)
        btn_register.pack(pady=10)
        
        # Initially populate the listbox with all students.
        self.populate_students_listbox(self.student_controller.get_all_students())

    def on_search(self, event):
        query = self.search_var.get().lower().strip()
        try:
            # Fetch all students from the database.
            all_students = self.student_controller.get_all_students()
            if query:
                filtered_students = [
                    student for student in all_students
                    if query in str(student["identificacion"]).lower() or 
                       query in student["nombre"].lower() or 
                       query in student["apellido"].lower()
                ]
            else:
                filtered_students = all_students
            self.populate_students_listbox(filtered_students)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al buscar alumnos: {e}")

    def populate_students_listbox(self, students):
        self.results_listbox.delete(0, tk.END)
        self.students_data = []  # Mapping between listbox indices and student data.
        for student in students:
            full_name = f"{student['identificacion']} - {student['nombre']} {student['apellido']}"
            self.results_listbox.insert(tk.END, full_name.title())
            self.students_data.append(student)

    def on_student_select(self, event):
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
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al seleccionar alumno: {e}")

    def register_payment(self):
        if not self.selected_student:
            messagebox.showwarning("Selección requerida", "Seleccione un alumno.")
            return
        amount_text = self.entry_amount.get().strip()
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
            self.selected_student["id"], amount, description
        )
        if success:
            formatted_student_name = f"{self.selected_student['nombre']} {self.selected_student['apellido']}".title()
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

        formatted_receipt = self.format_receipt_number(receipt_number, payment_date)
        pdf.cell(0, 10, f"Recibo Nº: {formatted_receipt}", ln=True)
        pdf.cell(0, 10, f"Fecha y Hora: {payment_date}", ln=True)
        pdf.cell(0, 10, f"Alumno: {student_name}", ln=True)

        formatted_amount = self.format_amount(amount)
        pdf.cell(0, 10, f"Monto: {formatted_amount}", ln=True)
        pdf.cell(0, 10, f"Descripción: {description}", ln=True)

        default_filename = f"recibo_{formatted_receipt}_{student_name.replace(' ', '_')}.pdf"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=default_filename,
            title="Guardar Recibo de Pago",
            filetypes=[("PDF files", "*.pdf")]
        )
        if file_path:
            pdf.output(file_path)
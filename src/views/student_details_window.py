import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import traceback
from fpdf import FPDF
from src.controllers.student_controller import StudentController
from src.controllers.payment_controller import PaymentController
from src.controllers.config_controller import ConfigController

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logo_path = os.path.join(BASE_DIR, "assets", "logo.png")

if not os.path.exists(logo_path):
    print(f"[WARNING] No se pudo cargar el logo: {logo_path}")
else:
    # Carga del logo...
    pass

class StudentDetailsWindow:
    def __init__(self, db, student_identification):
        self.db = db
        self.student_identification = student_identification
        self.student_controller = StudentController(self.db)
        self.payment_controller = PaymentController(self.db)
        # Instantiate the ConfigController to retrieve school configuration from the database.
        self.config_controller = ConfigController(self.db)
        # This will hold the student's details once loaded.
        self.student_details = {}
        # Create a new Toplevel window for this student's details.
        self.window = tk.Toplevel()
        self.window.title("Detalles del Estudiante")
        self.window.geometry("600x550")
        self.create_widgets()
        self.load_student_details()

    def create_widgets(self):
        # Main frame.
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(expand=True, fill="both")
        
        # Section for student information.
        info_frame = ttk.LabelFrame(main_frame, text="Información del Estudiante", padding=10)
        info_frame.pack(fill="x", pady=10)
        self.name_label = ttk.Label(info_frame, text="Nombre y Apellido: ")
        self.name_label.grid(row=0, column=0, sticky="w")
        self.id_label = ttk.Label(info_frame, text="Número de Identificación: ")
        self.id_label.grid(row=1, column=0, sticky="w")
        
        # Section for representative information.
        rep_frame = ttk.LabelFrame(main_frame, text="Información del Representante", padding=10)
        rep_frame.pack(fill="x", pady=10)
        self.rep_name_label = ttk.Label(rep_frame, text="Nombre del Representante: ")
        self.rep_name_label.grid(row=0, column=0, sticky="w")
        self.rep_phone_label = ttk.Label(rep_frame, text="Teléfono del Representante: ")
        self.rep_phone_label.grid(row=1, column=0, sticky="w")
        
        # Section for payment records.
        payments_frame = ttk.LabelFrame(main_frame, text="Historial de Pagos", padding=10)
        payments_frame.pack(expand=True, fill="both", pady=10)
        self.payments_tree = ttk.Treeview(payments_frame, columns=("fecha", "descripcion", "monto"), show="headings")
        self.payments_tree.heading("fecha", text="Fecha")
        self.payments_tree.heading("descripcion", text="Descripción")
        self.payments_tree.heading("monto", text="Monto")
        self.payments_tree.column("fecha", width=120)
        self.payments_tree.column("descripcion", width=280)
        self.payments_tree.column("monto", width=100, anchor="e")
        self.payments_tree.pack(expand=True, fill="both")
        # Bind double-click event to download receipt.
        self.payments_tree.bind("<Double-1>", self.download_receipt)

        # Button to download receipt.
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)
        self.btn_descargar = ttk.Button(btn_frame, text="Descargar Recibo", command=self.download_receipt)
        self.btn_descargar.pack(side="right", padx=5)

    def load_student_details(self):
        try:
            print(f"[DEBUG] Buscando detalles para el estudiante con identificación: {self.student_identification}")
            student = self.student_controller.get_student_by_identification(self.student_identification)
            print(f"[DEBUG] Datos del estudiante: {student}")
            if student:
                student_dict = dict(student)
                self.student_details = student_dict  # Store the student's details for receipt generation.
                full_name = f"{student_dict.get('nombre', '')} {student_dict.get('apellido', '')}"
                self.name_label.config(text=f"Nombre y Apellido: {full_name}")
                self.id_label.config(text=f"Número de Identificación: {student_dict.get('identificacion', 'N/A')}")
                
                rep_name = student_dict.get("representante", "N/A")
                rep_phone = student_dict.get("telefono", "N/A")
                self.rep_name_label.config(text=f"Nombre del Representante: {rep_name}")
                self.rep_phone_label.config(text=f"Teléfono del Representante: {rep_phone}")
                
                # Use internal student id (from the estudiantes table) to get payment history.
                internal_student_id = student_dict.get("id")
                print(f"[DEBUG] Usando ID interno del estudiante: {internal_student_id} para buscar pagos")
                payments = self.payment_controller.get_payments_by_student_identification(internal_student_id)
                print(f"[DEBUG] Historial de pagos: {payments}")
                for pago in payments:
                    pago_dict = dict(pago) if not isinstance(pago, dict) else pago
                    monto = pago_dict.get("amount", 0)
                    monto_formatted = f"{monto:,.2f}"
                    fecha = pago_dict.get("payment_date", "N/A")
                    descripcion = pago_dict.get("description", "")
                    payment_id = pago_dict.get("id")
                    self.payments_tree.insert("", "end", iid=str(payment_id), values=(fecha, descripcion, monto_formatted))
            else:
                messagebox.showerror("Error", "No se encontraron detalles para el estudiante.")
        except Exception as e:
            error_details = traceback.format_exc()
            messagebox.showerror("Error", f"Error al cargar detalles del estudiante:\n{error_details}")
            print(f"[ERROR] {error_details}")

    def generate_receipt_pdf(self, payment):
        pdf = FPDF()
        pdf.add_page()

        # Retrieve school configuration from the database.
        # Using get_all_configs() since get_school_config() is not defined.
        config = self.config_controller.get_all_configs()
        school_name = config.get("school_name", "Colegio Ejemplo")
        logo_path_config = config.get("logo_path", "assets/logo.png")

        # Insert logo using absolute path from the configuration.
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            logo_full_path = os.path.join(base_dir, logo_path_config)
            pdf.image(logo_full_path, x=10, y=8, w=33)
        except Exception as img_error:
            print(f"[WARNING] No se pudo cargar el logo: {img_error}")

        # Set up fonts and add School Name from the database configuration.
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, school_name, ln=True, align="C")
        pdf.ln(5)
        
        # Title of the receipt.
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Recibo de Pago", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", size=12)
        # Payment details.
        pdf.cell(50, 10, "Consecutivo:")
        pdf.cell(0, 10, str(payment.get("id", "N/A")), ln=True)
        
        pdf.cell(50, 10, "Fecha:")
        pdf.cell(0, 10, payment.get("payment_date", "N/A"), ln=True)
        
        pdf.cell(50, 10, "Descripción:")
        pdf.cell(0, 10, payment.get("description", ""), ln=True)
        
        monto = payment.get("amount", 0)
        pdf.cell(50, 10, "Monto:")
        pdf.cell(0, 10, f"{monto:,.2f}", ln=True)
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Detalles del Estudiante", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", size=12)
        # Student full name, identification, and representative.
        full_name = f"{self.student_details.get('nombre', '').capitalize()} {self.student_details.get('apellido', '').capitalize()}"
        pdf.cell(50, 10, "Estudiante:")
        pdf.cell(0, 10, full_name, ln=True)
        
        pdf.cell(50, 10, "Identificación:")
        pdf.cell(0, 10, self.student_details.get("identificacion", "N/A"), ln=True)
        
        pdf.cell(50, 10, "Representante:")
        pdf.cell(0, 10, self.student_details.get("representante", "N/A"), ln=True)
        
        return pdf

    def download_receipt(self, event=None):
        try:
            selected = self.payments_tree.selection()
            if not selected:
                messagebox.showwarning("Advertencia", "Seleccione un pago para descargar el recibo.")
                return
            payment_id = int(selected[0])
            payment = self.payment_controller.get_payment_by_id(payment_id)
            if not payment:
                messagebox.showerror("Error", "No se encontró la información del pago.")
                return
            save_path = filedialog.asksaveasfilename(
                title="Guardar Recibo",
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")]
            )
            if not save_path:
                return
            pdf = self.generate_receipt_pdf(dict(payment))
            pdf.output(save_path)
            messagebox.showinfo("Éxito", f"Recibo guardado en:\n{save_path}")
        except Exception as e:
            error_details = traceback.format_exc()
            messagebox.showerror("Error", f"Error al descargar el recibo:\n{error_details}")
            print(f"[ERROR] {error_details}")
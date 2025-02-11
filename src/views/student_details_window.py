import tkinter as tk
from tkinter import ttk, messagebox
import traceback
from src.controllers.student_controller import StudentController
from src.controllers.payment_controller import PaymentController

class StudentDetailsWindow:
    def __init__(self, db, student_identification):
        self.db = db
        self.student_identification = student_identification
        self.student_controller = StudentController(self.db)
        self.payment_controller = PaymentController(self.db)
        # Create a new Toplevel window for this student's details.
        self.window = tk.Toplevel()
        self.window.title("Detalles del Estudiante")
        self.window.geometry("500x400")
        self.create_widgets()
        self.load_student_details()

    def create_widgets(self):
        # Main frame
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
        self.payments_tree.column("fecha", width=100)
        self.payments_tree.column("descripcion", width=250)
        self.payments_tree.column("monto", width=80, anchor="e")
        self.payments_tree.pack(expand=True, fill="both")

    def load_student_details(self):
        try:
            # Debug: Print the identification used for lookup.
            print(f"[DEBUG] Buscando detalles para el estudiante con identificación: {self.student_identification}")
            student = self.student_controller.get_student_by_identification(self.student_identification)
            # Debug: Output the retrieved student data.
            print(f"[DEBUG] Datos del estudiante: {student}")
            if student:
                # Convert sqlite3.Row to dict so we can use .get() safely.
                student_dict = dict(student)
                full_name = f"{student_dict.get('nombre', '')} {student_dict.get('apellido', '')}"
                self.name_label.config(text=f"Nombre y Apellido: {full_name}")
                self.id_label.config(text=f"Número de Identificación: {student_dict.get('identificacion', 'N/A')}")
                
                # Retrieve representative details.
                rep_name = student_dict.get("representante", "N/A")
                rep_phone = student_dict.get("telefono", "N/A")
                self.rep_name_label.config(text=f"Nombre del Representante: {rep_name}")
                self.rep_phone_label.config(text=f"Teléfono del Representante: {rep_phone}")
                
                # Use internal student id (from the estudiantes table) to get payment history.
                internal_student_id = student_dict.get("id")
                print(f"[DEBUG] Usando ID interno del estudiante: {internal_student_id} para buscar pagos")
                payments = self.payment_controller.get_payments_by_student_identification(internal_student_id)
                # Debug: Output payment records.
                print(f"[DEBUG] Historial de pagos: {payments}")
                for pago in payments:
                    # Convert to dict if not already
                    pago_dict = dict(pago) if not isinstance(pago, dict) else pago
                    fecha = pago_dict.get("payment_date", "N/A")
                    descripcion = pago_dict.get("description", "")
                    monto = pago_dict.get("amount", 0)
                    self.payments_tree.insert("", "end", values=(fecha, descripcion, monto))
            else:
                messagebox.showerror("Error", "No se encontraron detalles para el estudiante.")
        except Exception as e:
            error_details = traceback.format_exc()
            messagebox.showerror("Error", f"Error al cargar detalles del estudiante:\n{error_details}")
            print(f"[ERROR] {error_details}")
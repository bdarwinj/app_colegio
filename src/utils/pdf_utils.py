# src/utils/pdf_utils.py
from fpdf import FPDF
import os
import datetime
from fpdf import FPDF


class PDFWithHeaderFooter(FPDF):
    def __init__(self, logo_path, school_name, receipt_number=""):
        super().__init__()
        self.logo_path = logo_path
        self.school_name = school_name
        self.receipt_number = receipt_number

    def header(self):
        # Insertar el logo
        if os.path.exists(self.logo_path):
            try:
                self.image(self.logo_path, x=10, y=8, w=25)  # Logo a la izquierda
            except Exception as e:
                print(f"Error al insertar logo: {e}")
        
        # Colocar el nombre del colegio al lado del logo
        self.set_xy(0, 8)  # X=40 para dejar espacio al logo, Y=8 para alinearlo
        self.set_font("Arial", "B", 18)  # Fuente en negrita, tamaño 18
        self.set_text_color(0, 51, 102)  # Color azul oscuro
        self.cell(0, 10, self.school_name, ln=True, align="C")  # Escribir el nombre
        
        # Título del reporte debajo
        self.set_xy(10, 20)  # Posición debajo del logo y nombre
        self.set_font("Arial", "B", 14)
        # Mostrar el recibo solo si se proporcionó un número
        if self.receipt_number:
            self.cell(0, 10, f"Recibo de Pago Nº {self.receipt_number}", ln=True, align="C")
        else: # Si no, solo mostrar el título
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
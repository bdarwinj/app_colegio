# src/views/pdf_common.py
from fpdf import FPDF
import os

def add_pdf_header(pdf, logo_path, school_name, header_title="Recibo de Pago"):
    """
    Agrega el encabezado al PDF con el logo, el nombre del colegio y un título.

    :param pdf: Objeto FPDF.
    :param logo_path: Ruta del logo.
    :param school_name: Nombre de la institución.
    :param header_title: Título del encabezado, por defecto "Recibo de Pago".
    """
    if logo_path and os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=10, y=8, w=30)
            pdf.ln(5)
        except Exception as e:
            # En caso de error al cargar la imagen, se continúa sin ella.
            pass
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, school_name, ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, header_title, ln=True)
    pdf.ln(5)

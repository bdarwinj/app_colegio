import os
import datetime
import openpyxl
from openpyxl.styles import Font
from openpyxl.drawing.image import Image as XLImage
from fpdf import FPDF

def export_students_to_excel(students, output_filename, school_name, logo_path):
    """
    Exports a list of student records to an Excel file.
    A header with the school name and school's logo (if available) is added.
    Each student record is expected to have the keys:
    identificacion, nombre, apellido, course_name, representante, telefono.
    The students are sorted by course_name (grado).
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Estudiantes"
    
    row_offset = 1
    # Add school name as header (merged across columns A-F)
    ws.merge_cells(start_row=row_offset, start_column=1, end_row=row_offset, end_column=6)
    header_cell = ws.cell(row=row_offset, column=1, value=school_name)
    header_cell.font = Font(bold=True, size=14)
    row_offset += 1
    
    # If logo exists, insert it in a nearby cell (e.g., G1)
    if os.path.exists(logo_path):
        try:
            img = XLImage(logo_path)
            img.height = 60
            img.width = 60
            ws.add_image(img, "G1")
        except Exception as e:
            print(f"Error al insertar logo en Excel: {e}")
    
    # Add an empty row after header
    row_offset += 1

    # Table headers for the student list
    headers = ["Numero de Identificacion", "Nombre", "Apellido", "Grado", "Representante", "Numero de Telefono"]
    ws.append(headers)
    
    # Make header bold
    header_row = row_offset + 1
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=header_row, column=col)
        cell.font = Font(bold=True)
    
    # Convert each sqlite3.Row to a dictionary (if needed) and sort by course_name
    students_as_dict = [dict(student) for student in students]
    students_sorted = sorted(students_as_dict, key=lambda x: x.get("course_name", ""))
    
    # Append student records starting after the header row
    for student in students_sorted:
        row = [
            student.get("identificacion", ""),
            student.get("nombre", ""),
            student.get("apellido", ""),
            student.get("course_name", ""),
            student.get("representante", ""),
            student.get("telefono", "")
        ]
        ws.append(row)
    
    wb.save(output_filename)
    return output_filename

def export_students_to_pdf(students, output_filename, school_name, logo_path):
    """
    Exports a list of student records to a PDF file.
    The PDF includes the school logo and name as header.
    Each record is expected to have the keys:
    identificacion, nombre, apellido, course_name, representante, telefono.
    """
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    
    # Insert school logo if available
    if os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=10, y=8, w=30)
        except Exception as e:
            print(f"Error al insertar logo en PDF: {e}")
    pdf.set_font("Arial", "B", 16)
    # Title with school name, centered.
    pdf.cell(0, 10, school_name, ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    headers = ["Numero de Identificacion", "Nombre", "Apellido", "Grado", "Representante", "Numero de Telefono"]
    col_widths = [40, 40, 40, 30, 60, 40]
    
    # Print table header row
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align="C")
    pdf.ln()
    
    pdf.set_font("Arial", "", 12)
    students_as_dict = [dict(student) for student in students]
    students_sorted = sorted(students_as_dict, key=lambda x: x.get("course_name", ""))
    
    for student in students_sorted:
        row = [
            str(student.get("identificacion", "")),
            student.get("nombre", ""),
            student.get("apellido", ""),
            student.get("course_name", ""),
            student.get("representante", ""),
            student.get("telefono", "")
        ]
        for i, data in enumerate(row):
            pdf.cell(col_widths[i], 10, data, border=1, align="C")
        pdf.ln()
    
    pdf.output(output_filename)
    return output_filename
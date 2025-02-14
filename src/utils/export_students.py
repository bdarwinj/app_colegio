import os
import datetime
import openpyxl
from openpyxl.styles import Font
from fpdf import FPDF

def export_students_to_excel(students, output_filename):
    """
    Exports a list of student records to an Excel file.
    Each student record is expected to have the keys:
    identificacion, nombre, apellido, course_name, representante, telefono.
    The students are sorted by course_name (grado).
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Estudiantes"
    
    # Define table header
    headers = ["Numero de Identificacion", "Nombre", "Apellido", "Grado", "Representante", "Numero de Telefono"]
    ws.append(headers)
    
    # Make header bold
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = Font(bold=True)
    
    # Convert each sqlite3.Row to a dictionary if necessary and sort students by course (grado)
    students_as_dict = [dict(student) for student in students]
    students_sorted = sorted(students_as_dict, key=lambda x: x.get("course_name", ""))
    
    # Append student rows
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

def export_students_to_pdf(students, output_filename):
    """
    Exports a list of student records to a PDF file.
    The PDF is formatted as a table with the columns:
    Numero de Identificacion, Nombre, Apellido, Grado, Representante, Numero de Telefono.
    The students are sorted by course (grado).
    """
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    
    # Define table headers and column widths (you can adjust these widths)
    headers = ["Numero de Identificacion", "Nombre", "Apellido", "Grado", "Representante", "Numero de Telefono"]
    col_widths = [40, 40, 40, 30, 60, 40]
    
    # Print header row
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align="C")
    pdf.ln()
    
    pdf.set_font("Arial", "", 12)
    
    # Convert each sqlite3.Row to a dictionary if necessary and sort students by course (grado)
    students_as_dict = [dict(student) for student in students]
    students_sorted = sorted(students_as_dict, key=lambda x: x.get("course_name", ""))
    
    # Print each student row
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
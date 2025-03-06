# src/utils/export_students.py
import os
import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import get_column_letter
from fpdf import FPDF
from itertools import groupby

# Clase para PDF con numeración en el pie de página
class PDFWithFooter(FPDF):
    def footer(self):
        self.set_y(-15)  # 15 mm desde el final de la página
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", 0, 0, "R")

# Constantes para los encabezados de la tabla de estudiantes
HEADERS = ["Identificacion", "Nombre", "Apellido", "Grado", "Representante", "Numero de Telefono"]

def _preparar_students(students):
    """
    Convierte cada registro de estudiante a diccionario y los ordena por curso,
    siguiendo la secuencia definida (de pre-jardin a once). Si existen cursos con
    el mismo nombre base, se ordenan alfabéticamente por el nombre completo.
    """
    prepared_students = []
    keys = ["id", "identificacion", "nombre", "apellido", "course_id", "representante", "telefono", "active"]
    
    for student in students:
        if isinstance(student, dict):
            prepared_students.append(student.copy())
        else:
            try:
                student_dict = dict(zip(keys, student))
                prepared_students.append(student_dict)
            except Exception as e:
                print(f"Error al convertir estudiante a diccionario: {e}")
                continue

    # Secuencia de cursos (en minúsculas)
    course_order = ["pre-jardin", "jardin", "transicion", "primero", "segundo", "tercero",
                    "cuarto", "quinto", "sexto", "septimo", "octavo", "noveno", "decimo", "once"]
    
    def course_sort_key(student):
        course = student.get("course_name", "")
        base = course.split("-")[0].strip().lower() if course else ""
        try:
            rank = course_order.index(base)
        except ValueError:
            rank = len(course_order)
        return (rank, course.lower())
    
    return sorted(prepared_students, key=course_sort_key)

def export_students_to_excel(students, output_filename, school_name, logo_path, course_controller):
    """
    Exporta estudiantes a un archivo Excel con hojas separadas por curso y una hoja 'Todos'.
    """
    wb = openpyxl.Workbook()
    students_sorted = _preparar_students(students)
    
    def get_course_name(student):
        """
        Obtiene el nombre del curso para un estudiante usando 'course_name' si existe,
        o consultando course_controller con 'course_id'.
        """
        if "course_name" in student and student["course_name"]:
            return student["course_name"]
        course_id = student.get("course_id", "")
        if course_id:
            try:
                course_data = course_controller.get_course_by_id(course_id)
                if course_data:
                    name = course_data.get("name", "")
                    seccion = course_data.get("seccion", "")
                    return f"{name} - {seccion.strip()}" if seccion and seccion.strip() else name
                return ""
            except Exception as e:
                print(f"Error al obtener nombre del curso para course_id {course_id}: {e}")
        return ""
    
    def _crear_hoja(wb, sheet_name, data):
        ws = wb.create_sheet(title=sheet_name)
        row_offset = 1
        # Título en la cabecera
        ws.merge_cells(start_row=row_offset, start_column=1, end_row=row_offset, end_column=6)
        header_cell = ws.cell(row=row_offset, column=1, value=school_name)
        header_cell.font = Font(bold=True, size=14)
        header_cell.alignment = Alignment(horizontal="center", vertical="center")
        row_offset += 1
        
        # Agregar logo si existe
        if os.path.exists(logo_path):
            try:
                img = XLImage(logo_path)
                img.height = 60
                img.width = 60
                ws.add_image(img, "G1")
            except Exception as e:
                print(f"Error al insertar logo en Excel: {e}")
        row_offset += 1
        
        # Encabezados de la tabla
        ws.append(HEADERS)
        header_row = ws.max_row
        header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
        thin_border = Border(left=Side(style="thin"), right=Side(style="thin"), 
                             top=Side(style="thin"), bottom=Side(style="thin"))
        for col in range(1, len(HEADERS) + 1):
            cell = ws.cell(row=header_row, column=col)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = header_fill
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Agregar registros de estudiantes
        for st in data:
            course_name_val = get_course_name(st)
            row_data = [
                st.get("identificacion", ""),
                st.get("nombre", ""),
                st.get("apellido", ""),
                course_name_val,
                st.get("representante", ""),
                st.get("telefono", "")
            ]
            ws.append(row_data)
        
        # Aplicar bordes
        for row in ws.iter_rows(min_row=header_row, max_row=ws.max_row, min_col=1, max_col=len(HEADERS)):
            for cell in row:
                cell.border = thin_border
        
        # Ajustar ancho de columnas dinámicamente
        for col in range(1, len(HEADERS) + 1):
            max_length = max(len(str(cell.value or "")) for cell in ws[get_column_letter(col)])
            ws.column_dimensions[get_column_letter(col)].width = max_length + 2
        
        return ws
    
    # Agrupar estudiantes por curso
    grouped_by_course = groupby(students_sorted, key=lambda s: get_course_name(s))
    for course_name, group in grouped_by_course:
        group_list = list(group)
        sheet_title = f"{course_name}" if course_name else "Grado_Desconocido"
        _crear_hoja(wb, sheet_title, group_list)
    
    default_sheet = wb.active
    wb.remove(default_sheet)
    _crear_hoja(wb, "Todos", students_sorted)
    
    wb.save(output_filename)
    return output_filename

def export_students_to_pdf(students, output_filename, school_name, logo_path, course_controller):
    """
    Exporta estudiantes a un archivo PDF ordenados por curso (pre-jardin a once),
    con numeración en el pie de página.
    """
    pdf = PDFWithFooter(orientation="L", unit="mm", format=(216, 385))
    pdf.add_page()
    
    if os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=10, y=8, w=30)
            pdf.ln(10)
        except Exception as e:
            print(f"Error al insertar logo en PDF: {e}")
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, school_name, ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_fill_color(79, 129, 189)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 12)
    col_widths = [len(header) * 3 for header in HEADERS]

    # Reutilizamos _preparar_students para ordenar
    students_sorted = _preparar_students(students)

    # Calcular anchos de columna dinámicamente
    for st in students_sorted:
        row_data = [
            str(st.get("identificacion", "")),
            str(st.get("nombre", "")),
            str(st.get("apellido", "")),
            st.get("course_name", ""),
            str(st.get("representante", "")),
            str(st.get("telefono", ""))
        ]
        for i, data in enumerate(row_data):
            content_width = len(data) * 3
            col_widths[i] = max(col_widths[i], content_width)

    # Encabezados en el PDF
    for i, header in enumerate(HEADERS):
        pdf.cell(col_widths[i], 10, header, border=1, align="C", fill=True)
    pdf.ln()
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 12)
    fill = False
    pdf.set_fill_color(240, 240, 240)
    
    for st in students_sorted:
        row_data = [
            str(st.get("identificacion", "")),
            str(st.get("nombre", "")),
            str(st.get("apellido", "")),
            st.get("course_name", ""),
            str(st.get("representante", "")),
            str(st.get("telefono", ""))
        ]
        for i, data in enumerate(row_data):
            pdf.cell(col_widths[i], 10, data, border=1, align="C", fill=fill)
        pdf.ln()
        fill = not fill
    
    pdf.output(output_filename)
    return output_filename
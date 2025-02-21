import os
import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import get_column_letter
from fpdf import FPDF
from itertools import groupby

# Constante para los encabezados de la tabla de estudiantes
HEADERS = ["Identificacion", "Nombre", "Apellido", "Grado", "Representante", "Numero de Telefono"]

def _preparar_students(students):
    """
    Convierte cada registro de estudiante a diccionario y los ordena
    por el campo 'course_id'.
    """
    return sorted([dict(student) for student in students], key=lambda x: x.get("course_id", ""))

def export_students_to_excel(students, output_filename, school_name, logo_path, course_controller):
    """
    Exporta una lista de registros de estudiantes a un archivo Excel.
    Se generan varias hojas (worksheets):
      - Una hoja para cada grado (course_id), con los estudiantes correspondientes.
      - Una hoja final con todos los estudiantes de todos los grados.
    
    Cada registro debe tener las claves:
      identificacion, nombre, apellido, course_id, representante, telefono.
    
    Se utiliza course_controller.get_course_by_id para obtener el nombre del curso.
    """
    wb = openpyxl.Workbook()
    
    # Prepara y ordena los estudiantes
    students_sorted = _preparar_students(students)
    
    # Función auxiliar para obtener el nombre del curso a partir del id
    def get_course_name(course_id):
        if course_id:
            course_data = course_controller.get_course_by_id(course_id)
            if course_data:
                return course_data.get("name", "")
        return ""
    
    # Función auxiliar para crear una hoja con estudiantes
    def _crear_hoja(wb, sheet_name, data):
        ws = wb.create_sheet(title=sheet_name)
        
        row_offset = 1
        
        # Agregar el nombre de la escuela como encabezado (combinado en columnas A-F)
        ws.merge_cells(start_row=row_offset, start_column=1, end_row=row_offset, end_column=6)
        header_cell = ws.cell(row=row_offset, column=1, value=school_name)
        header_cell.font = Font(bold=True, size=14)
        header_cell.alignment = Alignment(horizontal="center", vertical="center")
        row_offset += 1
        
        # Insertar logo si existe en la ruta especificada (en la celda G1)
        if os.path.exists(logo_path):
            try:
                img = XLImage(logo_path)
                img.height = 60
                img.width = 60
                ws.add_image(img, "G1")
            except Exception as e:
                print(f"Error al insertar logo en Excel: {e}")
        
        # Agregar una fila vacía después del encabezado
        row_offset += 1
        
        # Agregar los encabezados de la tabla
        ws.append(HEADERS)
        header_row = ws.max_row
        
        # Definir estilos para el encabezado de la tabla
        header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
        thin_border = Border(
            left=Side(style="thin"), 
            right=Side(style="thin"),
            top=Side(style="thin"), 
            bottom=Side(style="thin")
        )
        for col in range(1, len(HEADERS) + 1):
            cell = ws.cell(row=header_row, column=col)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = header_fill
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Agregar cada registro de estudiante, reemplazando "course_id" por el nombre del curso
        for st in data:
            course_id = st.get("course_id", "")
            course_name = get_course_name(course_id)
            row_data = [
                st.get("identificacion", ""),
                st.get("nombre", ""),
                st.get("apellido", ""),
                course_name,
                st.get("representante", ""),
                st.get("telefono", "")
            ]
            ws.append(row_data)
        
        # Aplicar borde a todas las celdas de la tabla
        for row in ws.iter_rows(min_row=header_row, max_row=ws.max_row, min_col=1, max_col=len(HEADERS)):
            for cell in row:
                cell.border = thin_border
        
        # Ajustar el ancho de cada columna según el contenido (encabezado o celdas)
        for col in range(1, len(HEADERS) + 1):
            max_length = 0
            col_letter = get_column_letter(col)
            for cell in ws[col_letter]:
                if cell.value is not None:
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
            ws.column_dimensions[col_letter].width = max_length + 2
        
        return ws
    
    # Crear hojas por cada grado (course_id)
    grouped_by_course = groupby(students_sorted, key=lambda s: s.get("course_id", ""))
    for course_id, group in grouped_by_course:
        group_list = list(group)
        sheet_name = f"Grado_{course_id}" if course_id else "Grado_Desconocido"
        _crear_hoja(wb, sheet_name, group_list)
    
    # Crear hoja final con todos los estudiantes ("Todos")
    default_sheet = wb.active
    wb.remove(default_sheet)
    _crear_hoja(wb, "Todos", students_sorted)
    
    wb.save(output_filename)
    return output_filename

def export_students_to_pdf(students, output_filename, school_name, logo_path, course_controller):
    """
    Exporta una lista de registros de estudiantes a un archivo PDF.
    El PDF incluye el logo y nombre de la escuela como encabezado.
    Cada registro debe tener las claves:
      identificacion, nombre, apellido, course_id, representante, telefono.
    
    Se utiliza course_controller.get_course_by_id para mostrar el nombre del curso.
    """
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    
    # Insertar el logo de la escuela si existe
    if os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=10, y=8, w=30)
            pdf.ln(10)
        except Exception as e:
            print(f"Error al insertar logo en PDF: {e}")
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, school_name, ln=True, align="C")
    pdf.ln(5)
    
    # Configurar colores para el encabezado de la tabla en el PDF
    pdf.set_fill_color(79, 129, 189)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 12)
    
    # Calcular anchos de columna en función del contenido
    col_widths = [len(header) * 3 for header in HEADERS]
    
    # Función auxiliar para obtener el nombre del curso
    def get_course_name(course_id):
        if course_id:
            course_data = course_controller.get_course_by_id(course_id)
            if course_data:
                return course_data.get("name", "")
        return ""
    
    # Preparar y ordenar la lista de estudiantes
    students_sorted = _preparar_students(students)
    for student in students_sorted:
        # Reemplazar course_id por el nombre del curso
        course_id = student.get("course_id", "")
        course_name = get_course_name(course_id)
        student["course_id"] = course_name
        row_data = [
            str(student.get("identificacion", "")),
            str(student.get("nombre", "")),
            str(student.get("apellido", "")),
            str(student.get("course_id", "")),
            str(student.get("representante", "")),
            str(student.get("telefono", ""))
        ]
        # Ajustar el ancho de las columnas según el contenido
        for i, data in enumerate(row_data):
            content_width = len(data) * 3
            if content_width > col_widths[i]:
                col_widths[i] = content_width
    
    # Agregar encabezados de la tabla con fondo coloreado
    for i, header in enumerate(HEADERS):
        pdf.cell(col_widths[i], 10, header, border=1, align="C", fill=True)
    pdf.ln()
    
    # Restablecer color de texto a negro para el contenido
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 12)
    
    # Color de fondo para filas alternas (gris claro)
    fill = False
    pdf.set_fill_color(240, 240, 240)
    
    # Agregar cada registro de estudiante con fondo alterno
    for student in students_sorted:
        row_data = [
            str(student.get("identificacion", "")),
            str(student.get("nombre", "")),
            str(student.get("apellido", "")),
            str(student.get("course_id", "")),
            str(student.get("representante", "")),
            str(student.get("telefono", ""))
        ]
        for i, data in enumerate(row_data):
            pdf.cell(col_widths[i], 10, data, border=1, align="C", fill=fill)
        pdf.ln()
        fill = not fill  # Alternar el fondo para cada fila
    
    pdf.output(output_filename)
    return output_filename

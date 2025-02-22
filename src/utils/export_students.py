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
    Convierte cada registro de estudiante a diccionario y los ordena por 'course_id'.
    Maneja diferentes formatos de entrada (diccionarios, tuplas, listas).
    """
    prepared_students = []
    keys = ["id", "identificacion", "nombre", "apellido", "course_id", "representante", "telefono", "active"]
    
    for student in students:
        if isinstance(student, dict):
            prepared_students.append(student.copy())  # Usar copia para no modificar el original
        else:
            # Si no es un diccionario, intenta convertirlo asumiendo un orden de claves
            try:
                student_dict = dict(zip(keys, student))
                prepared_students.append(student_dict)
            except Exception as e:
                print(f"Error al convertir estudiante a diccionario: {e}")
                continue
    
    return sorted(prepared_students, key=lambda x: x.get("course_id", ""))

def export_students_to_excel(students, output_filename, school_name, logo_path, course_controller):
    """
    Exporta una lista de registros de estudiantes a un archivo Excel.
    Genera varias hojas:
      - Una por cada grado (course_id) con los estudiantes correspondientes.
      - Una final con todos los estudiantes ("Todos").
    
    Cada registro debe tener las claves:
      identificacion, nombre, apellido, course_id (o nombre del curso), representante, telefono.
    Se usa course_controller.get_course_by_id para obtener el nombre del curso,
    concatenando el nombre y la sección (por ejemplo, "Tercero - A").
    """
    wb = openpyxl.Workbook()
    students_sorted = _preparar_students(students)
    
    # Función auxiliar para obtener el nombre completo del curso
    def get_course_name(student):
        # Si ya viene el nombre del curso, se usa directamente
        if "course_name" in student and student["course_name"]:
            return student["course_name"]
        # Sino, se obtiene desde course_id
        course_id = student.get("course_id", "")
        if course_id:
            try:
                course_data = course_controller.get_course_by_id(course_id)
                if course_data:
                    name = course_data.get("name", "")
                    seccion = course_data.get("seccion", "")
                    return f"{name} - {seccion}" if seccion else name
                return ""
            except Exception as e:
                print(f"Error al obtener nombre del curso para course_id {course_id}: {e}")
        return ""
    
    # Función auxiliar para crear una hoja de Excel
    def _crear_hoja(wb, sheet_name, data):
        ws = wb.create_sheet(title=sheet_name)
        row_offset = 1
        
        # Agregar el encabezado con el nombre de la escuela (combinado en columnas A-F)
        ws.merge_cells(start_row=row_offset, start_column=1, end_row=row_offset, end_column=6)
        header_cell = ws.cell(row=row_offset, column=1, value=school_name)
        header_cell.font = Font(bold=True, size=14)
        header_cell.alignment = Alignment(horizontal="center", vertical="center")
        row_offset += 1
        
        # Insertar logo si existe
        if os.path.exists(logo_path):
            try:
                img = XLImage(logo_path)
                img.height = 60
                img.width = 60
                ws.add_image(img, "G1")
            except Exception as e:
                print(f"Error al insertar logo en Excel: {e}")
        row_offset += 1
        
        # Agregar encabezados de la tabla
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
        
        # Agregar datos de estudiantes
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
        
        # Aplicar bordes a las celdas
        for row in ws.iter_rows(min_row=header_row, max_row=ws.max_row, min_col=1, max_col=len(HEADERS)):
            for cell in row:
                cell.border = thin_border
        
        # Ajustar ancho de columnas según el contenido
        for col in range(1, len(HEADERS) + 1):
            max_length = 0
            col_letter = get_column_letter(col)
            for cell in ws[col_letter]:
                if cell.value is not None:
                    cell_length = len(str(cell.value))
                    max_length = max(max_length, cell_length)
            ws.column_dimensions[col_letter].width = max_length + 2
        
        return ws
    
    # Crear hojas agrupadas por nombre completo del curso
    grouped_by_course = groupby(students_sorted, key=lambda s: get_course_name(s))
    for course_name, group in grouped_by_course:
        group_list = list(group)
        sheet_name = f"Grado_{course_name}" if course_name else "Grado_Desconocido"
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
    Incluye el logo y nombre de la escuela en el encabezado.
    Se utiliza course_controller.get_course_by_id para obtener el nombre completo del curso
    (concatenando el nombre y la sección, por ejemplo, "Tercero - A").
    """
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    
    # Insertar logo de la escuela si existe
    if os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=10, y=8, w=30)
            pdf.ln(10)
        except Exception as e:
            print(f"Error al insertar logo en PDF: {e}")
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, school_name, ln=True, align="C")
    pdf.ln(5)
    
    # Configurar encabezado de la tabla con fondo azul y texto blanco
    pdf.set_fill_color(79, 129, 189)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 12)
    col_widths = [len(header) * 3 for header in HEADERS]
    
    # Función auxiliar para obtener el nombre completo del curso
    def get_course_name(student):
        if "course_name" in student and student["course_name"]:
            return student["course_name"]
        course_id = student.get("course_id", "")
        if course_id:
            try:
                course_data = course_controller.get_course_by_id(course_id)
                if course_data:
                    name = course_data.get("name", "")
                    seccion = course_data.get("seccion", "")
                    return f"{name} - {seccion}" if seccion else name
                return ""
            except Exception as e:
                print(f"Error al obtener nombre del curso para course_id {course_id}: {e}")
        return ""
    
    # Preparar estudiantes y ajustar anchos de columna
    students_sorted = _preparar_students(students)
    for student in students_sorted:
        course_name_val = get_course_name(student)
        student["course_id"] = course_name_val  # Reemplazar course_id por el nombre completo del curso
        row_data = [
            str(student.get("identificacion", "")),
            str(student.get("nombre", "")),
            str(student.get("apellido", "")),
            course_name_val,
            str(student.get("representante", "")),
            str(student.get("telefono", ""))
        ]
        for i, data in enumerate(row_data):
            content_width = len(data) * 3
            col_widths[i] = max(col_widths[i], content_width)
    
    # Agregar encabezados de la tabla
    for i, header in enumerate(HEADERS):
        pdf.cell(col_widths[i], 10, header, border=1, align="C", fill=True)
    pdf.ln()
    
    # Restaurar color de texto a negro y establecer fuente para el contenido
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 12)
    fill = False
    pdf.set_fill_color(240, 240, 240)
    
    # Agregar cada registro de estudiante con filas alternas
    for student in students_sorted:
        row_data = [
            str(student.get("identificacion", "")),
            str(student.get("nombre", "")),
            str(student.get("apellido", "")),
            student.get("course_id", ""),
            str(student.get("representante", "")),
            str(student.get("telefono", ""))
        ]
        for i, data in enumerate(row_data):
            pdf.cell(col_widths[i], 10, data, border=1, align="C", fill=fill)
        pdf.ln()
        fill = not fill
    
    pdf.output(output_filename)
    return output_filename

# src/utils/export_students.py
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

def _assign_course_name(students, course_controller):
    """
    Asigna a cada estudiante la clave 'course_name' si no existe, utilizando course_controller.
    Retorna una nueva lista de estudiantes con course_name actualizado.
    """
    assigned = []
    for st in students:
        st_copy = st.copy()
        if "course_name" not in st_copy or not st_copy["course_name"]:
            course_id = st_copy.get("course_id", "")
            if course_id:
                try:
                    course_data = course_controller.get_course_by_id(course_id)
                    if course_data:
                        name = course_data.get("name", "")
                        seccion = course_data.get("seccion", "")
                        st_copy["course_name"] = f"{name} - {seccion}" if seccion else name
                    else:
                        st_copy["course_name"] = ""
                except Exception as e:
                    print(f"Error al obtener nombre del curso para course_id {course_id}: {e}")
                    st_copy["course_name"] = ""
        assigned.append(st_copy)
    return assigned

def _preparar_students(students):
    """
    Convierte cada registro de estudiante a diccionario y los ordena por curso,
    siguiendo la secuencia definida (de pre-jardin a once).
    Si existen cursos con el mismo nombre base, se ordenan alfabéticamente por el nombre completo.
    
    Retorna la lista final de estudiantes con la clave "course_name" asignada
    para que sea más fácil exportar.
    """
    prepared_students = []
    keys = ["id", "identificacion", "nombre", "apellido", "course_id", "representante", "telefono", "active"]
    
    for student in students:
        try:
            if isinstance(student, dict):
                prepared_students.append(student.copy())
            else:
                prepared_students.append(dict(zip(keys, student)))
        except Exception as e:
            print(f"Error al convertir estudiante a diccionario: {e}")
            continue

    # Definir la secuencia de cursos (en minúsculas) en orden ascendente
    course_order = [
        "pre-jardin", "jardin", "transicion", "primero", "segundo", "tercero",
        "cuarto", "quinto", "sexto", "septimo", "octavo", "noveno", "decimo", "once"
    ]
    
    def get_course_base(full_course_name):
        """
        Extrae la parte base del curso (ignorando la sección),
        por ejemplo "Primero" de "Primero - B", y lo retorna en minúsculas.
        """
        return full_course_name.split("-")[0].strip().lower() if full_course_name else ""
    
    def course_sort_key(st):
        """
        Determina la clave de ordenación en base al nombre del curso.
        1) rank según la secuencia course_order,
        2) nombre completo en minúsculas (para desempatarlos alfabéticamente).
        """
        course_name = st.get("course_name", "")
        base = get_course_base(course_name)
        try:
            rank = course_order.index(base)
        except ValueError:
            rank = len(course_order)  # Si no se encuentra, se va al final
        return (rank, course_name.lower())
    
    return sorted(prepared_students, key=course_sort_key)

def export_students_to_excel(students, output_filename, school_name, logo_path, course_controller):
    """
    Exporta una lista de registros de estudiantes a un archivo Excel.
    Genera varias hojas:
      - Una por cada grado (course_name) con los estudiantes correspondientes.
      - Una final con todos los estudiantes ("Todos").
    
    Cada registro debe tener las claves:
      identificacion, nombre, apellido, course_name (o se asigna dentro), representante, telefono.
    """
    wb = openpyxl.Workbook()
    
    # Asignar course_name a cada estudiante si no existe
    students_with_course_name = _assign_course_name(students, course_controller)
    
    # Ordenar estudiantes con la función _preparar_students
    students_sorted = _preparar_students(students_with_course_name)
    
    # Agrupar por course_name exacto (para hojas separadas)
    def group_key(st):
        return st.get("course_name", "")
    # groupby asume que la lista ya está ordenada según la clave, por eso se ordena de nuevo
    students_sorted_by_name = sorted(students_sorted, key=group_key)
    grouped = groupby(students_sorted_by_name, key=group_key)
    
    def _crear_hoja(wb, sheet_name, data):
        ws = wb.create_sheet(title=sheet_name)
        row_offset = 1
        
        # Encabezado con el nombre de la escuela
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
        
        for st in data:
            row_data = [
                st.get("identificacion", ""),
                st.get("nombre", ""),
                st.get("apellido", ""),
                st.get("course_name", ""),
                st.get("representante", ""),
                st.get("telefono", "")
            ]
            ws.append(row_data)
        
        for row in ws.iter_rows(min_row=header_row, max_row=ws.max_row, min_col=1, max_col=len(HEADERS)):
            for cell in row:
                cell.border = thin_border
        
        for col in range(1, len(HEADERS) + 1):
            max_length = 0
            col_letter = get_column_letter(col)
            for cell in ws[col_letter]:
                if cell.value is not None:
                    cell_length = len(str(cell.value))
                    max_length = max(max_length, cell_length)
            ws.column_dimensions[col_letter].width = max_length + 2

    # Crear una hoja por cada course_name
    for course_name, group in grouped:
        group_list = list(group)
        sheet_name = f"{course_name}" if course_name else "Grado_Desconocido"
        _crear_hoja(wb, sheet_name, group_list)
    
    # Crear hoja final con todos los estudiantes ("Todos")
    default_sheet = wb.active
    wb.remove(default_sheet)
    _crear_hoja(wb, "Todos", students_sorted)
    
    wb.save(output_filename)
    return output_filename

def export_students_to_pdf(students, output_filename, school_name, logo_path, course_controller):
    """
    Exporta una lista de registros de estudiantes a un archivo PDF, ordenados según la secuencia
    (pre-jardin hasta once). Si hay cursos con la misma base, se ordena alfabéticamente.
    """
    pdf = FPDF(orientation="L", unit="mm", format=(216, 385))
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
    
    # Asignar course_name a cada estudiante si no existe
    students_with_course_name = _assign_course_name(students, course_controller)
    
    # Ordenar usando _preparar_students
    students_sorted = _preparar_students(students_with_course_name)
    
    # Ajustar el ancho de columnas
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
            if content_width > col_widths[i]:
                col_widths[i] = content_width
    
    # Encabezados
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
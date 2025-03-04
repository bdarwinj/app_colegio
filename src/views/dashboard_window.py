# src/views/dashboard_window.py
import tkinter as tk
from tkinter import ttk
import datetime

class DashboardWindow(tk.Toplevel):
    def __init__(self, parent, student_controller, course_controller, payment_controller):
        """
        Ventana de Dashboard que muestra estadísticas del sistema:
         - Número de cursos totales
         - Número de cursos con alumnos
         - Número total de alumnos
         - Número de alumnos por curso
         - Total dinero recogido en el mes
         - Total dinero recogido en el año
         - Alumnos sin pago en el mes actual
        """
        super().__init__(parent)
        self.title("Dashboard - Estadísticas")
        self.geometry("600x500")
        
        self.student_controller = student_controller
        self.course_controller = course_controller
        self.payment_controller = payment_controller
        
        self.create_widgets()
        self.load_stats()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(expand=True, fill="both")

        self.label_title = ttk.Label(self.main_frame, text="Dashboard de Estadísticas", font=("Arial", 16, "bold"))
        self.label_title.pack(pady=5)

        self.stats_text = tk.Text(self.main_frame, height=20, width=70, state="disabled")
        self.stats_text.pack(pady=5, fill="both", expand=True)
        
    def load_stats(self):
        """
        Carga las estadísticas y las muestra en el Text widget.
        """
        # Limpiar el Text
        self.stats_text.configure(state="normal")
        self.stats_text.delete("1.0", tk.END)

        # 1. Número de cursos totales
        all_courses = self.course_controller.get_all_courses()
        total_courses = len(all_courses)

        # 2. Número de cursos con alumnos
        #   - Buscamos los course_id de todos los alumnos y contamos cuántos cursos distintos hay
        all_students = self.student_controller.get_all_students()
        course_ids_in_use = set(stu["course_name"] for stu in all_students if stu.get("course_name"))
        courses_with_students = len(course_ids_in_use)

        # 3. Número total de alumnos
        total_students = len(all_students)

        # 4. Número de alumnos por curso
        #    - Creamos un conteo {course_name: cantidad}
        course_count_map = {}
        for stu in all_students:
            c_name = stu.get("course_name", "N/A")
            course_count_map[c_name] = course_count_map.get(c_name, 0) + 1
        
        # 5. Dinero recogido en el mes actual
        #   - Filtramos pagos del mes actual
        current_month = datetime.datetime.now().strftime("%Y-%m")
        payments_month = self.payment_controller.get_payments_in_month(current_month)
        total_month = sum(pay["amount"] for pay in payments_month if pay["amount"])

        # 6. Dinero recogido en el año actual
        current_year = datetime.datetime.now().year
        payments_year = self.payment_controller.get_payments_in_year(current_year)
        total_year = sum(pay["amount"] for pay in payments_year if pay["amount"])

        # 7. Alumnos sin pago en el mes actual
        #   - Obtenemos la lista de student_id que han pagado en el mes
        student_ids_paid_this_month = set(pay["student_id"] for pay in payments_month)
        #   - Filtramos a los que NO están en esa lista
        students_without_payment_this_month = [stu for stu in all_students if stu["id"] not in student_ids_paid_this_month]

        # Construir el texto a mostrar
        info = []
        info.append(f"Número total de cursos: {total_courses}")
        info.append(f"Número de cursos con alumnos: {courses_with_students}")
        info.append(f"Número total de alumnos: {total_students}")
        
        info.append("\nAlumnos por curso:")
        for c_name, count in course_count_map.items():
            info.append(f"  - {c_name}: {count}")
        
        info.append(f"\nDinero recogido en el mes (fecha {current_month}): {total_month}")
        info.append(f"Dinero recogido en el año {current_year}: {total_year}")
        
        info.append(f"\nAlumnos sin pago en el mes actual: {len(students_without_payment_this_month)}")
        if len(students_without_payment_this_month) > 0:
            info.append("Lista de alumnos sin pago este mes:")
            for stu in students_without_payment_this_month:
                full_name = f"{stu['nombre']} {stu['apellido']}".strip()
                info.append(f"  - {stu['identificacion']} | {full_name}")
        
        # Mostrar en el Text
        final_text = "\n".join(info)
        self.stats_text.insert(tk.END, final_text)
        self.stats_text.configure(state="disabled")

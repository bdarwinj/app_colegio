# src/controllers/course_fee_controller.py
import sqlite3
from src.utils.db_utils import db_cursor
from src.logger import logger

class CourseFeeController:
    def __init__(self, db):
        self.db = db

    def set_fee(self, course_id, academic_year, fee):
        """
        Establece o actualiza la tarifa (mensualidad) para un curso en un año académico específico.
        """
        try:
            query_update = "UPDATE course_fees SET fee = ? WHERE course_id = ? AND academic_year = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query_update, (fee, course_id, academic_year))
                if cursor.rowcount == 0:
                    query_insert = "INSERT INTO course_fees (course_id, academic_year, fee) VALUES (?, ?, ?)"
                    cursor.execute(query_insert, (course_id, academic_year, fee))
            return True, "Tarifa establecida/actualizada correctamente."
        except sqlite3.Error as e:
            logger.exception("Error al establecer la tarifa del curso")
            return False, f"Error al establecer la tarifa: {e}"

    def get_fee(self, course_id, academic_year):
        """
        Obtiene la tarifa para un curso en un año académico.
        """
        try:
            query = "SELECT fee FROM course_fees WHERE course_id = ? AND academic_year = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (course_id, academic_year))
                row = cursor.fetchone()
            if row:
                return row["fee"]
            return None
        except sqlite3.Error as e:
            logger.exception("Error al obtener la tarifa del curso")
            return None

    def get_all_fees(self, academic_year):
        """
        Obtiene todas las tarifas para un año académico dado.
        Retorna una lista de diccionarios con course_id, academic_year y fee.
        """
        try:
            query = "SELECT * FROM course_fees WHERE academic_year = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (academic_year,))
                rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.exception("Error al obtener todas las tarifas")
            return []

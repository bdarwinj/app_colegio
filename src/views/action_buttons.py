import tkinter as tk
from tkinter import ttk

class ActionButtons(ttk.Frame):
    def __init__(self, parent, refresh_command, pdf_command, excel_command, pdf_export_command):
        super().__init__(parent)
        self.refresh_command = refresh_command
        self.pdf_command = pdf_command
        self.excel_command = excel_command
        self.pdf_export_command = pdf_export_command
        self.create_widgets()

    def create_widgets(self):
        self.btn_refrescar = ttk.Button(self, text="Refrescar Lista", command=self.refresh_command)
        self.btn_refrescar.pack(side="left", padx=5)
        self.btn_pdf = ttk.Button(self, text="Generar Paz y Salvo", command=self.pdf_command)
        self.btn_pdf.pack(side="left", padx=5)
        self.btn_export_excel = ttk.Button(self, text="Exportar a Excel", command=self.excel_command)
        self.btn_export_excel.pack(side="left", padx=5)
        self.btn_export_pdf = ttk.Button(self, text="Exportar a PDF", command=self.pdf_export_command)
        self.btn_export_pdf.pack(side="left", padx=5)
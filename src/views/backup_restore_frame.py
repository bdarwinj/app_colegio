import tkinter as tk
from tkinter import ttk

class BackupRestoreFrame(ttk.Frame):
    def __init__(self, parent, backup_command, restore_command, enrollments_command):
        super().__init__(parent)
        self.backup_command = backup_command
        self.restore_command = restore_command
        self.enrollments_command = enrollments_command
        self.create_widgets()

    def create_widgets(self):
        btn_backup = ttk.Button(self, text="Backup DB", command=self.backup_command)
        btn_backup.pack(side="left", padx=5)
        btn_restore = ttk.Button(self, text="Restaurar DB", command=self.restore_command)
        btn_restore.pack(side="left", padx=5)
        self.btn_manage_enrollments = ttk.Button(self, text="Gestionar Inscripciones", command=self.enrollments_command)
        self.btn_manage_enrollments.pack(side="left", padx=5)
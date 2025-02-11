import tkinter as tk
from tkinter import ttk, messagebox
from src.controllers.user_controller import UserController

class UserManagementUI:
    def __init__(self, db):
        self.db = db
        self.user_controller = UserController(self.db)
        self.window = tk.Toplevel()
        self.window.title("Administrar Usuarios")
        self.window.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.window, padding=10)
        frame.pack(expand=True, fill="both")
        
        ttk.Label(frame, text="Nombre de Usuario:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_username = ttk.Entry(frame, width=30)
        self.entry_username.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Contraseña:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_password = ttk.Entry(frame, show="*", width=30)
        self.entry_password.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Rol:").grid(row=2, column=0, sticky="w", pady=5)
        self.combo_role = ttk.Combobox(frame, state="readonly", values=["admin", "user"], width=28)
        self.combo_role.grid(row=2, column=1, pady=5)
        self.combo_role.current(1)  # Default to "user"
        
        btn_create = ttk.Button(frame, text="Crear Usuario", command=self.create_user)
        btn_create.grid(row=3, column=0, columnspan=2, pady=15)

    def create_user(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        role = self.combo_role.get().strip()
        if not username or not password or not role:
            messagebox.showwarning("Campos incompletos", "Por favor, complete todos los campos.")
            return
        
        success, msg = self.user_controller.create_user(username, password, role)
        if success:
            messagebox.showinfo("Éxito", msg)
            self.entry_username.delete(0, tk.END)
            self.entry_password.delete(0, tk.END)
        else:
            messagebox.showerror("Error", msg)
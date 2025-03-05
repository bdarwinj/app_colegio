# src/views/user_management_ui.py
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
        self.window.transient()  
        self.window.grab_set()   
        self.center_window(400, 300)
        self.create_widgets()
        self.load_users()

    def center_window(self, width, height):
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        frame = ttk.Frame(self.window, padding=10)
        frame.pack(expand=True, fill="both")
        
        # Formulario para crear usuario
        ttk.Label(frame, text="Nombre de Usuario:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_username = ttk.Entry(frame, width=30)
        self.entry_username.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Contraseña:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_password = ttk.Entry(frame, show="*", width=30)
        self.entry_password.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Rol:").grid(row=2, column=0, sticky="w", pady=5)
        self.combo_role = ttk.Combobox(frame, state="readonly", values=["admin", "user"], width=28)
        self.combo_role.grid(row=2, column=1, pady=5)
        self.combo_role.current(1)
        
        btn_create = ttk.Button(frame, text="Crear Usuario", command=self.create_user)
        btn_create.grid(row=3, column=0, columnspan=2, pady=15)
        
        # Separador
        ttk.Separator(frame, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Listado de usuarios
        self.tree = ttk.Treeview(frame, columns=("username", "role"), show="headings", height=5)
        self.tree.heading("username", text="Usuario")
        self.tree.heading("role", text="Rol")
        self.tree.column("username", width=150, anchor="center")
        self.tree.column("role", width=100, anchor="center")
        self.tree.grid(row=5, column=0, columnspan=2, pady=5, sticky="nsew")
        self.tree.bind("<Double-1>", self.on_user_double_click)
        
        frame.rowconfigure(5, weight=1)

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
            self.load_users()
        else:
            messagebox.showerror("Error", msg)

    def load_users(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            query = "SELECT username, role FROM users"
            from src.utils.db_utils import db_cursor
            with db_cursor(self.db) as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
            for row in rows:
                self.tree.insert("", tk.END, values=(row["username"], row["role"]))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar usuarios: {e}")

    def on_user_double_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        username = item["values"][0]
        from src.views.change_user_password_window import ChangeUserPasswordWindow
        ChangeUserPasswordWindow(self.window, username, self.user_controller)

if __name__ == "__main__":
    import sqlite3
    db = sqlite3.connect("colegio.db")
    db.row_factory = sqlite3.Row
    root = tk.Tk()
    root.withdraw()
    ui = UserManagementUI(db)
    root.mainloop()

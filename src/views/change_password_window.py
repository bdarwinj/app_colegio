import tkinter as tk
from tkinter import ttk, messagebox
import traceback

class ChangePasswordWindow:
    def __init__(self, master, user_controller, current_user):
        """
        master: the parent Tkinter window.
        user_controller: an instance of UserController to handle the password change.
        current_user: the username (or other identifier) of the logged-in user.
        """
        self.master = master
        self.user_controller = user_controller
        self.current_user = current_user
        self.window = tk.Toplevel(master)
        self.window.title("Cambiar Clave")
        self.window.geometry("400x250")
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.window, padding="20")
        frame.pack(expand=True, fill="both")
        
        # Old password
        ttk.Label(frame, text="Clave Actual:").grid(row=0, column=0, sticky="w", pady=5)
        self.old_password_entry = ttk.Entry(frame, show="*")
        self.old_password_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # New password
        ttk.Label(frame, text="Nueva Clave:").grid(row=1, column=0, sticky="w", pady=5)
        self.new_password_entry = ttk.Entry(frame, show="*")
        self.new_password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Confirm new password
        ttk.Label(frame, text="Confirmar Nueva Clave:").grid(row=2, column=0, sticky="w", pady=5)
        self.confirm_password_entry = ttk.Entry(frame, show="*")
        self.confirm_password_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Change Button
        self.change_password_button = ttk.Button(frame, text="Cambiar Clave", command=self.change_password)
        self.change_password_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        frame.columnconfigure(1, weight=1)

    def change_password(self):
        old_password = self.old_password_entry.get().strip()
        new_password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        
        if not old_password or not new_password or not confirm_password:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return
        
        if new_password != confirm_password:
            messagebox.showerror("Error", "La nueva clave y su confirmación no coinciden.")
            return
        
        try:
            # Call the method to change password for the current user.
            success, message = self.user_controller.change_password(self.current_user, old_password, new_password)
            if success:
                messagebox.showinfo("Éxito", message)
                self.window.destroy()
            else:
                messagebox.showerror("Error", message)
        except Exception:
            messagebox.showerror("Error", f"Error al cambiar clave:\n{traceback.format_exc()}")
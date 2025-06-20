# login.py
import tkinter as tk
from tkinter import messagebox
import sqlite3
import re
import os
import subprocess
from PIL import Image, ImageTk

# ---------------- DATABASE SETUP ----------------
conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT,
        mobile TEXT
    )
''')

# ---------------- VALIDATION ----------------
def is_valid_email(email):
    return re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

def is_valid_mobile(mobile):
    return re.fullmatch(r'^\d{10}$', mobile)

# ---------------- MAIN APP ----------------
class LoginRegisterApp:
    def __init__(self, root, user_data=None, edit_mode=False, on_back=None):
        self.root = root
        self.user_data = user_data or {}
        self.edit_mode = edit_mode
        self.on_back = on_back
        self.logo = None
        self.setup_ui()

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = int(screen_width * 0.6)
        height = int(screen_height * 0.6)
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        self.root.title("Inventory Login/Register")
        self.root.configure(bg="#a5dbe9")
        self.center_window()
        if self.edit_mode:
            self.show_register()
        else:
            self.show_login()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def load_logo(self):
        try:
            image_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
            image = Image.open(image_path).convert("RGBA")
            image = image.resize((120, 120))
            self.logo = ImageTk.PhotoImage(image)
            logo_label = tk.Label(self.root, image=self.logo, bg="#a5dbe9")
            logo_label.pack(pady=(10, 10))
        except Exception as e:
            print("Logo load failed:", e)

    def style_entry(self, entry):
        entry.config(relief="solid", bd=1, bg="white", highlightthickness=1, highlightbackground="#ccc")

    def show_login(self):
        self.clear_screen()
        self.load_logo()

        tk.Label(self.root, text="Welcome Back!", font=("Segoe UI", 24, "bold"),
                 bg="#a5dbe9", fg="#003344").pack(pady=5)

        frame = tk.Frame(self.root, bg="#ffffff", bd=1, relief="solid")
        frame.pack(pady=10, ipadx=20, ipady=10)

        tk.Label(frame, text="Username:", font=("Segoe UI", 12), bg="#ffffff").grid(row=0, column=0, pady=15, padx=15, sticky='e')
        self.login_username = tk.Entry(frame, font=("Segoe UI", 12), width=30)
        self.login_username.grid(row=0, column=1, pady=15, padx=15)
        self.style_entry(self.login_username)

        tk.Label(frame, text="Password:", font=("Segoe UI", 12), bg="#ffffff").grid(row=1, column=0, pady=15, padx=15, sticky='e')
        self.login_password = tk.Entry(frame, show="*", font=("Segoe UI", 12), width=30)
        self.login_password.grid(row=1, column=1, pady=15, padx=15)
        self.style_entry(self.login_password)

        tk.Button(self.root, text="Login", font=("Segoe UI", 12, "bold"), bg="#0077b6", fg="white",
                  padx=15, pady=8, command=self.login_user).pack(pady=25)

        tk.Label(self.root, text="Don't have an account?", bg="#a5dbe9", font=("Segoe UI", 11)).pack()
        tk.Button(self.root, text="Go to Register", font=("Segoe UI", 10, "bold"),
                  command=self.show_register, bg="#ffffff").pack(pady=5)

    def show_register(self):
        self.clear_screen()
        self.load_logo()

        title = "Edit Profile" if self.edit_mode else "Create Account"
        tk.Label(self.root, text=title, font=("Segoe UI", 24, "bold"),
                 bg="#a5dbe9", fg="#003344").pack(pady=10)

        frame = tk.Frame(self.root, bg="#ffffff", bd=1, relief="solid", padx=30, pady=10)
        frame.pack()

        labels = ["Username", "Password", "Confirm Password", "Email", "Mobile No"]
        entries = []

        for i, label in enumerate(labels):
            tk.Label(frame, text=f"{label}:", font=("Segoe UI", 12), bg="#ffffff").grid(row=i, column=0, pady=12, sticky='e', padx=10)
            entry = tk.Entry(frame, font=("Segoe UI", 12), width=30, show="*" if "Password" in label else "")
            entry.grid(row=i, column=1, pady=12, padx=10)
            self.style_entry(entry)
            entries.append(entry)

        self.reg_username, self.reg_password, self.reg_confirm, self.reg_email, self.reg_mobile = entries

        if self.edit_mode:
            self.reg_username.insert(0, self.user_data.get("username", ""))
            self.reg_username.config(state="disabled")
            self.reg_password.insert(0, self.user_data.get("password", ""))
            self.reg_confirm.insert(0, self.user_data.get("password", ""))
            self.reg_email.insert(0, self.user_data.get("email", ""))
            self.reg_mobile.insert(0, self.user_data.get("mobile", ""))

        action_text = "Save Changes" if self.edit_mode else "Register"
        action_command = self.update_user if self.edit_mode else self.register_user

        tk.Button(self.root, text=action_text, font=("Segoe UI", 12, "bold"), bg="#0077b6", fg="white",
                  padx=15, pady=8, command=action_command).pack(pady=20)

        if not self.edit_mode:
            tk.Label(self.root, text="Already have an account?", bg="#a5dbe9", font=("Segoe UI", 11)).pack()
            tk.Button(self.root, text="Go to Login", font=("Segoe UI", 10, "bold"),
                      command=self.show_login, bg="#ffffff").pack(pady=5)
        elif self.on_back:
            tk.Button(self.root, text="Back", font=("Segoe UI", 10), command=self.on_back).pack(pady=5)

    def login_user(self):
        username = self.login_username.get()
        password = self.login_password.get()

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        result = cursor.fetchone()

        if result:
            messagebox.showinfo("Login Success", f"Welcome {username}!")
            self.root.destroy()
            subprocess.Popen(["python", "main.py", username])
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def register_user(self):
        username = self.reg_username.get()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()
        email = self.reg_email.get()
        mobile = self.reg_mobile.get()

        if not username or not password or not confirm or not email or not mobile:
            messagebox.showwarning("Empty Fields", "Please fill all fields.")
            return
        if password != confirm:
            messagebox.showerror("Password Error", "Passwords do not match.")
            return
        if not is_valid_email(email):
            messagebox.showerror("Invalid Email", "Please enter a valid email address.")
            return
        if not is_valid_mobile(mobile):
            messagebox.showerror("Invalid Mobile", "Enter a 10-digit mobile number.")
            return

        try:
            cursor.execute("INSERT INTO users (username, password, email, mobile) VALUES (?, ?, ?, ?)",
                           (username, password, email, mobile))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful. You can login now.")
            self.show_login()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")

    def update_user(self):
        username = self.user_data.get("username")
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()
        email = self.reg_email.get()
        mobile = self.reg_mobile.get()

        if not password or not confirm or not email or not mobile:
            messagebox.showwarning("Empty Fields", "Please fill all fields.")
            return
        if password != confirm:
            messagebox.showerror("Password Error", "Passwords do not match.")
            return
        if not is_valid_email(email):
            messagebox.showerror("Invalid Email", "Please enter a valid email address.")
            return
        if not is_valid_mobile(mobile):
            messagebox.showerror("Invalid Mobile", "Enter a 10-digit mobile number.")
            return

        try:
            cursor.execute("UPDATE users SET password=?, email=?, mobile=? WHERE username=?",
                           (password, email, mobile, username))
            conn.commit()
            messagebox.showinfo("Success", "Profile updated successfully.")
            if self.on_back:
                self.on_back()
        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))















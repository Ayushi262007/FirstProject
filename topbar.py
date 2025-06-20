# topbar.py
from tkinter import *
import sqlite3
import os
from PIL import Image, ImageTk
import login

def create_topbar(parent, username, switch_to_register_callback=None):
    def show_profile_info(event):
        profile_window = Toplevel(parent)
        profile_window.title("User Profile")
        profile_window.geometry("300x240")
        profile_window.configure(bg="#ffffff")
        profile_window.resizable(False, False)

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT email, mobile, password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            email, mobile, password = result
        else:
            email, mobile, password = "N/A", "N/A", ""

        user_info = {
            "Username": username,
            "Email": email,
            "Phone": mobile
        }

        Label(profile_window, text="👤 Profile", font=("Arial", 16, "bold"), bg="#ffffff", fg="#2c3e50").pack(pady=(10, 5))
        for key, value in user_info.items():
            frame = Frame(profile_window, bg="#ffffff")
            frame.pack(anchor="w", padx=20, pady=5)
            Label(frame, text=f"{key}:", font=("Arial", 11, "bold"), bg="#ffffff", fg="#34495e").pack(side=LEFT)
            Label(frame, text=value, font=("Arial", 11), bg="#ffffff", fg="#34495e").pack(side=LEFT, padx=10)

        def edit_profile():
            profile_window.destroy()
            root = Tk()
            login.LoginRegisterApp(root, user_data={"username": username, "email": email, "mobile": mobile, "password": password}, edit_mode=True, on_back=root.destroy)
            root.mainloop()

        Button(profile_window, text="Edit", command=edit_profile,
               bg="#2980b9", fg="white", font=("Arial", 10, "bold")).pack(pady=(10, 5))

        Button(profile_window, text="Close", command=profile_window.destroy,
               bg="#e74c3c", fg="white", font=("Arial", 10)).pack(pady=(5, 10))

    topbar = Frame(parent, bg="#ffffff", height=60)
    topbar.grid(row=0, column=0, columnspan=2, sticky="ew")
    topbar.grid_propagate(False)

    try:
        logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
        logo_img = Image.open(logo_path).resize((45, 45))
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = Label(topbar, image=logo_photo, bg="#ffffff", bd=0)
        logo_label.image = logo_photo
        logo_label.pack(side=LEFT, padx=(15, 10), pady=5)
    except Exception as e:
        print("Topbar logo load failed:", e)

    Label(topbar, text="📦 Inventory Management System", bg="#ffffff", fg="#2c3e50", font=("Arial", 15, "bold")).pack(side=LEFT)

    profile_icon = Label(topbar, text="👤", bg="#ffffff", font=("Arial", 16), cursor="hand2")
    profile_icon.pack(side=RIGHT, padx=15)
    profile_icon.bind("<Button-1>", show_profile_info)







#leftbar.py

from tkinter import *

def create_left_sidebar(parent, nav_callbacks):
    sidebar = Frame(parent, bg="#021E3A", width=200)
    sidebar.grid(row=1, column=0, sticky="nsew")
    sidebar.grid_propagate(False)

    # Configure rows for equal vertical spacing
    for i in range(9):  # 1 for title + 7 buttons + 1 extra bottom space
        sidebar.rowconfigure(i, weight=1)

    # Section Title
    Label(
        sidebar, text="Navigation", bg="#021E3A", fg="white",
        font=("Segoe UI", 16, "bold"), pady=10
    ).grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

    # Navigation Buttons
    buttons = [
        ("Dashboard", nav_callbacks.get("Dashboard")),
        ("Add Product", nav_callbacks.get("Add Product")),
        ("View Inventory", nav_callbacks.get("View Inventory")),
        ("Purchase Requests", nav_callbacks.get("Purchase Requests")),
        ("Expiry Alerts", nav_callbacks.get("Expiry Alerts")),
        ("Warehouses", nav_callbacks.get("Warehouses")),
        ("Logout", nav_callbacks.get("Logout")),
    ]

    for idx, (label, command) in enumerate(buttons):
        btn = Button(
            sidebar, text=label, font=("Segoe UI", 12),
            bg="#0c3d5e", fg="white", bd=0,
            activebackground="#4ef1d1", activeforeground="#ffffff",
            command=command if command else lambda: print(f"{label} not linked"),
            padx=10, pady=8
        )
        btn.grid(row=idx + 1, column=0, sticky="ew", padx=20, pady=2)

    return sidebar
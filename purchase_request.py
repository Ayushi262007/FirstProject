#purchase_request.py

from tkinter import *
from tkinter import messagebox
import json
import os
from datetime import datetime
from storage import load_inventory

REQUEST_FILE = "requests.json"
LOW_STOCK_THRESHOLD = 5

def load_requests():
    if os.path.exists(REQUEST_FILE):
        with open(REQUEST_FILE, "r") as file:
            try:
                data = json.load(file)
                # Normalize entries
                cleaned = []
                for req in data:
                    name = req.get("product_name") or req.get("name")
                    qty = req.get("requested_qty") or req.get("quantity")
                    status = req.get("status", "Pending").capitalize()
                    date = req.get("date", datetime.now().strftime("%Y-%m-%d"))

                    if name and qty:
                        cleaned.append({
                            "product_name": name,
                            "requested_qty": int(qty),
                            "status": status,
                            "date": str(date)
                        })
                return cleaned
            except Exception as e:
                print("[Error] Failed to load requests:", e)
                return []
    return []

def save_requests(requests):
    with open(REQUEST_FILE, "w") as file:
        json.dump(requests, file, indent=4)

def auto_generate_requests():
    inventory = load_inventory()
    existing = load_requests()
    existing_names = [req["product_name"] for req in existing if req["status"] == "Pending"]

    new_requests = []
    for item in inventory:
        if item.get("quantity", 0) < LOW_STOCK_THRESHOLD and item.get("name", "") not in existing_names:
            new_requests.append({
                "product_name": item.get("name", ""),
                "requested_qty": LOW_STOCK_THRESHOLD - item.get("quantity", 0),
                "status": "Pending",
                "date": datetime.now().strftime("%Y-%m-%d")
            })

    all_requests = existing + new_requests
    save_requests(all_requests)
    return all_requests

def update_status(index, new_status, refresh_callback):
    requests = load_requests()
    if 0 <= index < len(requests):
        requests[index]["status"] = new_status
        save_requests(requests)
        refresh_callback()

def add_manual_request(name, qty, refresh_callback):
    if not name or not qty:
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return

    try:
        qty = int(qty)
    except ValueError:
        messagebox.showwarning("Invalid Quantity", "Enter a valid number.")
        return

    requests = load_requests()
    requests.append({
        "product_name": name,
        "requested_qty": qty,
        "status": "Pending",
        "date": datetime.now().strftime("%Y-%m-%d")
    })
    save_requests(requests)
    refresh_callback()

def create_purchase_request(parent):
    frame = Frame(parent, bg="#ecf0f1")
    frame.grid(row=0, column=0, sticky="nsew")

   
    # Manual Entry Section
    manual_label = Label(frame, text="➕ Manual Purchase Request", font=("Segoe UI", 12, "bold"), bg="#ecf0f1")
    manual_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))

    # Labels for Name and Qty
    Label(frame, text="Name:", bg="#ecf0f1").grid(row=1, column=0, sticky="w", padx=(10, 5))
    Label(frame, text="Qty:", bg="#ecf0f1").grid(row=1, column=1, sticky="w", padx=(10, 5))

    # Entry fields
    entry_name = Entry(frame, width=25)
    entry_qty = Entry(frame, width=10)
    entry_name.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="w")
    entry_qty.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    add_btn = Button(frame, text="Add Request", bg="#2980b9", fg="white",
                     command=lambda: add_manual_request(entry_name.get(), entry_qty.get(), refresh_table))
    add_btn.grid(row=2, column=2, padx=5, pady=5)


    separator = Frame(frame, height=2, bd=1, relief=SUNKEN, bg="gray")
    separator.grid(row=3, column=0, columnspan=5, sticky="ew", padx=10, pady=10)

    table_label = Label(frame, text="📋 Purchase Requests", font=("Segoe UI", 12, "bold"), bg="#ecf0f1")
    table_label.grid(row=4, column=0, sticky="w", padx=10, pady=(5, 2))

    table_frame = Frame(frame, bg="#ecf0f1")
    table_frame.grid(row=5, column=0, columnspan=5, sticky="nsew", padx=10)

    def refresh_table():
        for widget in table_frame.winfo_children():
            widget.destroy()

        requests = auto_generate_requests()

        headers = ["#", "Product Name", "Quantity", "Date", "Status", "Actions"]
        for col, header in enumerate(headers):
            Label(table_frame, text=header, font=("Segoe UI", 10, "bold"), bg="#dcdde1", width=15).grid(row=0, column=col, padx=1, pady=1)

        for i, req in enumerate(requests):
            Label(table_frame, text=str(i + 1), bg="white", width=5).grid(row=i+1, column=0)
            Label(table_frame, text=req["product_name"], bg="white").grid(row=i+1, column=1)
            Label(table_frame, text=req["requested_qty"], bg="white").grid(row=i+1, column=2)
            Label(table_frame, text=req["date"], bg="white").grid(row=i+1, column=3)
            Label(table_frame, text=req["status"], bg="white").grid(row=i+1, column=4)

            action_frame = Frame(table_frame, bg="white")
            action_frame.grid(row=i+1, column=5)

            if req["status"] == "Pending":
                Button(action_frame, text="Approve", bg="#27ae60", fg="white",
                       command=lambda idx=i: update_status(idx, "Approved", refresh_table)).pack(side=LEFT, padx=2)
            elif req["status"] == "Approved":
                Button(action_frame, text="Mark as Ordered", bg="#8e44ad", fg="white",
                       command=lambda idx=i: update_status(idx, "Ordered", refresh_table)).pack(side=LEFT, padx=2)
            else:
                Label(action_frame, text="✔ Done", fg="green", bg="white").pack()

    refresh_table()
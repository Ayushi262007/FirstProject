import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

WAREHOUSE_FILE = "warehouse_data.json"

def load_warehouses():
    if not os.path.exists(WAREHOUSE_FILE):
        return []
    with open(WAREHOUSE_FILE, "r") as f:
        return json.load(f)

def save_warehouses(data):
    with open(WAREHOUSE_FILE, "w") as f:
        json.dump(data, f, indent=4)

selected_products = []

def create_warehouse_module(root):
    global selected_products
    selected_products = []
    warehouses = load_warehouses()
    selected_target = tk.StringVar()

    for widget in root.winfo_children():
        widget.destroy()

    frame = tk.Frame(root, bg="#f0f0f0")
    frame.pack(fill="both", expand=True)

    # Controls
    controls = tk.Frame(frame, bg="#ddd", pady=10)
    controls.pack(fill="x")

    tk.Label(controls, text="Selected:", font=("Arial", 12)).pack(side="left", padx=10)
    selected_label = tk.Label(controls, text="0 items", font=("Arial", 12, "bold"), fg="blue")
    selected_label.pack(side="left")

    ttk.Label(controls, text="→").pack(side="left", padx=(30, 5))
    target_dropdown = ttk.Combobox(controls, textvariable=selected_target, state="readonly", width=15)
    target_dropdown.pack(side="left", padx=5)

    ttk.Button(controls, text="Move", command=lambda: move_products(warehouses, selected_label, selected_target)).pack(side="left", padx=5)
    ttk.Button(controls, text="Remove Product", command=lambda: remove_selected_product(warehouses, selected_label)).pack(side="left", padx=5)

    ttk.Button(controls, text="Remove", command=lambda: remove_warehouse(warehouses)).pack(side="right", padx=10)
    ttk.Button(controls, text="Add", command=lambda: add_warehouse(warehouses)).pack(side="right", padx=5)

    warehouse_container = tk.Frame(frame, bg="#f0f0f0")
    warehouse_container.pack()

    def refresh_view():
        nonlocal warehouses
        warehouses = load_warehouses()
        target_dropdown['values'] = [w['name'] for w in warehouses]
        for widget in warehouse_container.winfo_children():
            widget.destroy()

        for index, warehouse in enumerate(warehouses):
            box = tk.Frame(warehouse_container, bd=2, relief="groove", bg="white", padx=10, pady=10)
            box.grid(row=0, column=index, padx=20, pady=20)

            tk.Label(box, text=warehouse["name"], font=("Arial", 14, "bold")).pack()

            seat_container = tk.Frame(box, bg="#e0e0e0", padx=5, pady=5)
            seat_container.pack(pady=10)

            for i, product in enumerate(warehouse.get("products", [])):
                bg_color = get_color(product)

                is_selected = any(p["product"] == product and p["source"]["id"] == warehouse["id"] for p in selected_products)
                border_color = "#3399ff" if is_selected else "black"

                seat = tk.Label(
                    seat_container,
                    text=f"{product['name']}\n{product['quantity']}/{product.get('capacity', product['quantity'])}",
                    width=12,
                    height=4,
                    bg=bg_color,
                    bd=3,
                    relief="solid",
                    wraplength=80,
                    highlightbackground=border_color,
                    highlightthickness=2
                )
                seat.grid(row=i // 2, column=i % 2, padx=5, pady=5)

                def toggle(p=product, w=warehouse):
                    handle_selection(p, w)
                    selected_label.config(text=f"{len(selected_products)} items")
                    refresh_view()

                seat.bind("<Button-1>", lambda e, p=product, w=warehouse: toggle(p, w))

    def handle_selection(product, source):
        global selected_products
        entry = {"product": product, "source": source}

        for sp in selected_products:
            if sp["product"] == product and sp["source"]["id"] == source["id"]:
                selected_products.remove(sp)
                return

        if selected_products and selected_products[0]["source"]["id"] != source["id"]:
            selected_products.clear()

        selected_products.append(entry)

    def move_products(warehouses, label, selected_target):
        global selected_products

        if not selected_products or not selected_target.get():
            messagebox.showwarning("Select Items", "Please select products and target warehouse.")
            return

        target_name = selected_target.get()
        source = selected_products[0]["source"]
        target = next((w for w in warehouses if w["name"] == target_name), None)

        if not target or target["id"] == source["id"]:
            messagebox.showwarning("Invalid Target", "Please select a different warehouse.")
            return

        blocked = []
        moved = []

        for entry in selected_products:
            product = entry["product"]
            qty = product.get("quantity", 0)
            name = product.get("name", "")
            capacity = product.get("capacity", qty)

            source_wh = next((w for w in warehouses if w["id"] == source["id"]), None)
            target_wh = next((w for w in warehouses if w["id"] == target["id"]), None)

            if not source_wh or not target_wh:
                continue

            existing_target = next((p for p in target_wh["products"] if p["name"] == name), None)
            move_qty = qty

            if existing_target:
                remaining = existing_target["capacity"] - existing_target["quantity"]
                if remaining <= 0:
                    blocked.append(f"{name} (no space)")
                    continue
                move_qty = min(qty, remaining)
                existing_target["quantity"] += move_qty
            else:
                move_qty = min(qty, capacity)
                target_wh["products"].append({
                    "name": name,
                    "quantity": move_qty,
                    "capacity": capacity
                })

            remaining_qty = qty - move_qty
            updated_products = []
            for p in source_wh["products"]:
                if p == product:
                    if remaining_qty > 0:
                        p["quantity"] = remaining_qty
                        updated_products.append(p)
                else:
                    updated_products.append(p)
            source_wh["products"] = updated_products

            if move_qty > 0:
                moved.append(f"{name} (+{move_qty})")
            if remaining_qty > 0:
                blocked.append(f"{name} ({remaining_qty} not moved)")

        save_warehouses(warehouses)
        selected_products.clear()
        selected_target.set("")
        label.config(text="0 items")

        msg = ""
        if moved:
            msg += f"✅ Moved:\n" + "\n".join(moved)
        if blocked:
            msg += f"\n❌ Skipped or Partially Moved:\n" + "\n".join(blocked)

        messagebox.showinfo("Transfer Result", msg.strip())
        refresh_view()

    def remove_selected_product(warehouses, label):
        global selected_products
        if not selected_products:
            messagebox.showinfo("Remove Product", "No product selected.")
            return
        removed = []
        for entry in selected_products:
            product = entry["product"]
            source = entry["source"]
            for wh in warehouses:
                if wh["id"] == source["id"]:
                    wh["products"] = [p for p in wh["products"] if p != product]
                    removed.append(product["name"])
        save_warehouses(warehouses)
        selected_products.clear()
        label.config(text="0 items")
        messagebox.showinfo("Removed", f"Removed: {', '.join(removed)}")
        refresh_view()

    def get_color(product):
        qty = product.get("quantity", 0)
        cap = product.get("capacity", qty)
        ratio = qty / cap if cap else 0
        if ratio >= 1:
            return "#ff4c4c"
        elif ratio >= 0.5:
            return "#ffcc00"
        else:
            return "#66cc66"

    def add_warehouse(warehouses):
        name = simpledialog.askstring("Add Warehouse", "Enter warehouse name:")
        if not name:
            return
        if any(w["name"] == name for w in warehouses):
            messagebox.showerror("Duplicate", "Warehouse already exists.")
            return
        wid = f"W{len(warehouses)+1}"
        warehouses.append({
            "id": wid,
            "name": name,
            "products": []
        })
        save_warehouses(warehouses)
        refresh_view()

    def remove_warehouse(warehouses):
        names = [w["name"] for w in warehouses]
        if not names:
            messagebox.showinfo("No Warehouses", "No warehouses to remove.")
            return
        name = simpledialog.askstring("Remove Warehouse", "Enter warehouse name to remove:")
        if name not in names:
            messagebox.showerror("Not Found", "Warehouse not found.")
            return
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete warehouse '{name}'?"):
            warehouses = [w for w in warehouses if w["name"] != name]
            save_warehouses(warehouses)
            refresh_view()

    refresh_view()








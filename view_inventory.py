# view_inventory.py
from tkinter import *
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import json, os
from storage import load_inventory, save_inventory, save_purchase_requests, load_requests

LOW_STOCK_THRESHOLD = 10
WAREHOUSE_FILE = "warehouse_data.json"

def load_warehouses():
    if not os.path.exists(WAREHOUSE_FILE):
        return []
    with open(WAREHOUSE_FILE, "r") as f:
        return json.load(f)

def save_warehouses(data):
    with open(WAREHOUSE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def create_view_inventory(parent, get_inventory_data=load_inventory, switch_to_module=None):
    frame = Frame(parent, bg="#ecf0f1", padx=20, pady=20)
    frame.pack(fill=BOTH, expand=True)

    Label(frame, text="📋 View Inventory", font=("Segoe UI", 16, "bold"),
          bg="#ecf0f1", fg="#2c3e50").pack(anchor="w", pady=(0, 10))

    btn_frame = Frame(frame, bg="#ecf0f1")
    btn_frame.pack(anchor="w", pady=(0, 10))

    def refresh_table():
        for i in tree.get_children():
            tree.delete(i)
        for item in get_inventory_data():
            insert_inventory_row(item)

    def is_expired(expiry_date):
        try:
            return datetime.strptime(expiry_date, "%Y-%m-%d") < datetime.now()
        except:
            return False

    def insert_inventory_row(item):
        quantity = item.get("quantity", 0)
        expiry_date = item.get("expiry_date", item.get("expiry", ""))

        values = (
            item.get("product_id", ""),
            item.get("name", ""),
            item.get("category", ""),
            quantity,
            f"{float(item.get('unit_price', 0)):,.2f}",
            expiry_date,
            item.get("supplier", "")
        )

        tag = ""
        if quantity < LOW_STOCK_THRESHOLD:
            tag = "low_stock"
        elif expiry_date and is_expired(expiry_date):
            tag = "expired"

        tree.insert("", END, values=values, tags=(tag,))

    def add_product():
        if switch_to_module:
            switch_to_module("add_product")

    def edit_selected_product():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product to edit.")
            return

        product_id = tree.item(selected[0])['values'][0]

        if switch_to_module:
            switch_to_module("edit_product", product_id)

    def delete_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select product(s) to delete.")
            return

        inventory = load_inventory()
        selected_ids = [tree.item(i)['values'][0] for i in selected]
        updated_inventory = [item for item in inventory if item.get("product_id") not in selected_ids]

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {len(selected_ids)} product(s)?")
        if not confirm:
            return

        save_inventory(updated_inventory)
        refresh_table()
        messagebox.showinfo("Deleted", "Selected products have been removed.")

    def add_to_purchase_requests():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select at least one product.")
            return

        selected_items = []
        for item_id in selected:
            row = tree.item(item_id)['values']
            product_name = row[1]
            try:
                requested_qty = int(row[3])
            except ValueError:
                requested_qty = 1

            selected_items.append({
                "product_name": product_name,
                "requested_qty": requested_qty,
                "status": "Pending",
                "date": datetime.now().strftime("%Y-%m-%d")
            })

        existing_requests = load_requests()
        existing_requests.extend(selected_items)
        save_purchase_requests(existing_requests)

        messagebox.showinfo("Added", "Selected items added to purchase requests.")

    def add_to_warehouse():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select at least one product.")
            return

        warehouses = load_warehouses()
        if not warehouses:
            messagebox.showerror("Unavailable", "No warehouses available. Please create one first.")
            return

        invalid_items = []
        for item_id in selected:
            row = tree.item(item_id)['values']
            name = row[1]
            try:
                quantity = int(row[3])
            except:
                quantity = 0
            expiry_date = row[5]
            if is_expired(expiry_date):
                invalid_items.append(f"{name} (expired)")
            elif quantity <= 0:
                invalid_items.append(f"{name} (zero qty)")

        if invalid_items:
            messagebox.showwarning("Cannot Proceed", "These items cannot be added:\n" + "\n".join(invalid_items))
            return

        popup = Toplevel()
        popup.title("Add to Warehouse")
        popup.geometry("300x200")
        popup.transient(tree)

        Label(popup, text="Choose Target Warehouse:", font=("Segoe UI", 11)).pack(pady=10)
        warehouse_var = StringVar()
        warehouse_cb = ttk.Combobox(popup, textvariable=warehouse_var, state="readonly")
        warehouse_cb['values'] = [w["name"] for w in warehouses]
        warehouse_cb.pack(pady=5)

        def confirm_add():
            name = warehouse_var.get()
            if not name:
                messagebox.showwarning("Missing", "Please select a warehouse.")
                return

            warehouse = next((w for w in warehouses if w["name"] == name), None)
            if not warehouse:
                messagebox.showerror("Error", "Warehouse not found.")
                return

            added = []

            for item_id in selected:
                row = tree.item(item_id)['values']
                name = row[1]
                quantity = int(row[3])

                existing = next((p for p in warehouse["products"] if p["name"] == name), None)
                if existing:
                    remaining_capacity = existing["capacity"] - existing["quantity"]
                    if remaining_capacity <= 0:
                        continue
                    prompt_qty = simpledialog.askinteger(
                        "Capacity Limit",
                        f"{name} has {remaining_capacity} units space.\nEnter quantity to move:",
                        minvalue=1, maxvalue=remaining_capacity
                    )
                    if prompt_qty:
                        existing["quantity"] += prompt_qty
                        added.append(f"{name} (+{prompt_qty})")
                else:
                    prompt_qty = simpledialog.askinteger(
                        "New Product",
                        f"Enter quantity to add for new product {name}:",
                        minvalue=1, maxvalue=quantity
                    )
                    if prompt_qty:
                        warehouse["products"].append({
                            "name": name,
                            "quantity": prompt_qty,
                            "capacity": quantity
                        })
                        added.append(f"{name} (+{prompt_qty})")

            save_warehouses(warehouses)
            popup.destroy()

        Button(popup, text="Add to Warehouse", command=confirm_add,
               bg="#27ae60", fg="white", padx=10, pady=5).pack(pady=20)

    # Buttons
    Button(btn_frame, text="➕ Add Product", command=add_product,
           bg="#27ae60", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)

    Button(btn_frame, text="✏ Edit", command=edit_selected_product,
           bg="#2980b9", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)

    Button(btn_frame, text="🗑 Delete", command=delete_selected,
           bg="#c0392b", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)

    Button(btn_frame, text="🛒 Request", command=add_to_purchase_requests,
           bg="#d35400", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)

    Button(btn_frame, text="📦 Add to Warehouse", command=add_to_warehouse,
           bg="#8e44ad", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)

    # Table
    table_frame = Frame(frame)
    table_frame.pack(fill=BOTH, expand=True)

    cols = ("Product ID", "Name", "Category", "Quantity", "Unit Price", "Expiry Date", "Supplier")
    tree = ttk.Treeview(table_frame, columns=cols, show="headings")
    tree.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar = Scrollbar(table_frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=RIGHT, fill=Y)

    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=110, anchor="center")

    tree.tag_configure("low_stock", background="#ffeaa7")
    tree.tag_configure("expired", background="#fab1a0")

    refresh_table()
    return frame
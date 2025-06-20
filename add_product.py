from tkinter import *
from tkinter import messagebox
from storage import load_inventory, save_inventory

def style_entry(entry):
    entry.config(
        font=("Segoe UI", 13),
        bd=0,
        highlightthickness=1,
        highlightbackground="#2980b9",
        highlightcolor="#1c6aa3",
        relief="flat",
        bg="white",
        insertbackground="#2c3e50",
        width=34
    )

def create_add_product(frame):
    frame.configure(bg="#a5dbe9")
    for widget in frame.winfo_children():
        widget.destroy()

    container = Frame(frame, bg="#a5dbe9")
    container.place(relx=0.5, rely=0, relwidth=0.6, relheight=1, anchor="n")

    Label(container, text="➕ Add New Product", font=("Segoe UI", 26, "bold"),
          bg="#a5dbe9", fg="#2c3e50").pack(pady=(40, 10))

    form_frame = Frame(container, bg="#a5dbe9")
    form_frame.pack(pady=10)

    labels = [
        "Product ID", "Product Name", "Category", "Quantity",
        "Unit Price", "Expiry Date (YYYY-MM-DD)", "Supplier"
    ]
    entries = []

    for i, label in enumerate(labels):
        Label(form_frame, text=label, font=("Segoe UI", 14, "bold"),
              bg="#a5dbe9", fg="#2c3e50", anchor="e", width=26).grid(row=i, column=0, sticky="e", pady=12, padx=5)
        entry = Entry(form_frame)
        style_entry(entry)
        entry.grid(row=i, column=1, sticky="w", pady=10, padx=(0, 20), ipady=6 )
        entries.append(entry)

    id_entry, name_entry, category_entry, quantity_entry, price_entry, expiry_entry, sup_entry = entries

    def add_product():
        product_id = id_entry.get().strip()
        name = name_entry.get().strip()
        category = category_entry.get().strip()
        quantity = quantity_entry.get().strip()
        price = price_entry.get().strip()
        expiry_date = expiry_entry.get().strip()
        supplier = sup_entry.get().strip()

        if not product_id or not name or not category or not quantity or not price or not expiry_date or not supplier:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be an integer and price must be a number.")
            return

        inventory = load_inventory()

        for item in inventory:
            if item.get("product_id", "").lower() == product_id.lower():
                messagebox.showwarning("Duplicate ID", f"Product ID '{product_id}' already exists.")
                return
            if item.get("name", "").lower() == name.lower():
                messagebox.showwarning("Duplicate Product", f"Product '{name}' already exists.")
                return

        product = {
            "product_id": product_id,
            "name": name,
            "category": category,
            "quantity": quantity,
            "unit_price": price,
            "expiry": expiry_date,
            "supplier": supplier
        }

        inventory.append(product)
        save_inventory(inventory)
        messagebox.showinfo("Success", f"✅ Product '{name}' added successfully!")

        for entry in entries:
            entry.delete(0, END)

    Button(container, text="➕ Add Product", command=add_product,
           bg="#2980b9", fg="white", font=("Segoe UI", 14, "bold"),
           activebackground="#2471a3", relief="flat", padx=24, pady=12, cursor="hand2").pack(pady=30)


def create_edit_product_form(frame, product_id, back_callback=None):
    frame.configure(bg="#a5dbe9")
    for widget in frame.winfo_children():
        widget.destroy()

    container = Frame(frame, bg="#a5dbe9")
    container.place(relx=0.5, rely=0, relwidth=0.6, relheight=1, anchor="n")

    Label(container, text="✏ Edit Product", font=("Segoe UI", 26, "bold"),
          bg="#a5dbe9", fg="#2c3e50").pack(pady=(40, 10))

    form_frame = Frame(container, bg="#a5dbe9")
    form_frame.pack(pady=10)

    labels = [
        "Product ID", "Product Name", "Category", "Quantity",
        "Unit Price", "Expiry Date (YYYY-MM-DD)", "Supplier"
    ]
    entries = []

    for i, label in enumerate(labels):
        Label(form_frame, text=label, font=("Segoe UI", 14, "bold"),
              bg="#a5dbe9", fg="#2c3e50", anchor="e", width=22).grid(row=i, column=0, sticky="e", pady=12, padx=5)
        entry = Entry(form_frame)
        style_entry(entry)
        entry.grid(row=i, column=1, sticky="w", pady=12, padx=(0, 30))
        entries.append(entry)

    id_entry, name_entry, category_entry, quantity_entry, price_entry, expiry_entry, sup_entry = entries
    inventory = load_inventory()
    product = next((item for item in inventory if item.get("product_id") == product_id), None)

    if not product:
        messagebox.showerror("Error", "Product not found.")
        return

    id_entry.insert(0, product.get("product_id", ""))
    name_entry.insert(0, product.get("name", ""))
    category_entry.insert(0, product.get("category", ""))
    quantity_entry.insert(0, product.get("quantity", ""))
    price_entry.insert(0, product.get("unit_price", ""))
    expiry_entry.insert(0, product.get("expiry", ""))
    sup_entry.insert(0, product.get("supplier", ""))
    id_entry.config(state=DISABLED)

    button_frame = Frame(container, bg="#a5dbe9")
    button_frame.pack(pady=30)

    def save_changes():
        name = name_entry.get().strip()
        category = category_entry.get().strip()
        quantity = quantity_entry.get().strip()
        price = price_entry.get().strip()
        expiry_date = expiry_entry.get().strip()
        supplier = sup_entry.get().strip()

        if not name or not category or not quantity or not price or not expiry_date or not supplier:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be an integer and price a number.")
            return

        for item in inventory:
            if item.get("product_id") == product_id:
                item.update({
                    "name": name,
                    "category": category,
                    "quantity": quantity,
                    "unit_price": price,
                    "expiry": expiry_date,
                    "supplier": supplier
                })
                break

        save_inventory(inventory)
        messagebox.showinfo("Success", "✅ Product updated successfully!")

        if back_callback:
            back_callback()

    Button(button_frame, text="📅 Save Changes", command=save_changes,
           bg="#2980b9", fg="white", font=("Segoe UI", 14, "bold"),
           activebackground="#2471a3", relief="flat", padx=24, pady=12, cursor="hand2").pack(side=RIGHT, padx=10)

    if back_callback:
        Button(button_frame, text="⬅ Back", command=back_callback,
               bg="#95a5a6", fg="white", font=("Segoe UI", 14, "bold"),
               activebackground="#7f8c8d", relief="flat", padx=24, pady=12, cursor="hand2").pack(side=LEFT, padx=10)





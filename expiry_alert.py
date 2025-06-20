from tkinter import * 
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from storage import load_inventory, save_inventory

def create_expiry_alert(parent):
    alert_frame = Frame(parent, bg="#f6f6f6", padx=20, pady=20)
    alert_frame.pack(fill=BOTH, expand=True)

    Label(alert_frame, text="⚠ Expiry Alerts", font=("Segoe UI", 16, "bold"),
          bg="#f6f6f6", fg="#c0392b").pack(anchor="w", pady=(0, 10))

    filter_frame = Frame(alert_frame, bg="#f6f6f6")
    filter_frame.pack(anchor="w", pady=(0, 10))

    Label(filter_frame, text="Filter:", font=("Segoe UI", 10), bg="#f6f6f6").pack(side=LEFT)

    filter_option = StringVar()
    filter_option.set("7 Days")  # ✅ Explicitly set default option
    OptionMenu(filter_frame, filter_option, "7 Days", "30 Days", "Expired").pack(side=LEFT, padx=5)

    # Table frame
    table_frame = Frame(alert_frame)
    table_frame.pack(fill=BOTH, expand=True)

    cols = ("Product ID", "Name", "Quantity", "Expiry Date", "Status")
    tree = ttk.Treeview(table_frame, columns=cols, show="headings")
    tree.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar = Scrollbar(table_frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=RIGHT, fill=Y)

    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")

    tree.tag_configure("expired", background="#ffcccc")

    def get_filtered_items():
        inventory = load_inventory()
        today = datetime.now().date()
        days = 7 if filter_option.get() == "7 Days" else 30

        filtered = []
        for item in inventory:
            expiry_str = item.get("expiry_date", item.get("expiry", ""))
            try:
                expiry = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            except:
                continue

            if filter_option.get() == "Expired" and expiry < today:
                status = "Expired"
            elif today <= expiry <= today + timedelta(days=days):
                status = "Expiring Soon"
            else:
                continue

            filtered.append({
                "product_id": item.get("product_id"),
                "name": item.get("name"),
                "quantity": item.get("quantity"),
                "expiry_date": expiry_str,
                "status": status
            })
        return sorted(filtered, key=lambda x: x["expiry_date"])

    def refresh_table():
        for i in tree.get_children():
            tree.delete(i)

        data = get_filtered_items()
        for row in data:
            tag = "expired" if row["status"] == "Expired" else ""
            tree.insert("", END, values=(
                row["product_id"],
                row["name"],
                row["quantity"],
                row["expiry_date"],
                row["status"]
            ), tags=(tag,))

    def archive_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select expired item(s) to delete.")
            return

        names = [tree.item(i)['values'][1] for i in selected]
        item_list = "\n".join(names)
        confirm = messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove the following item(s)?\n\n{item_list}")
        if not confirm:
            return

        inventory = load_inventory()
        selected_ids = [tree.item(i)['values'][0] for i in selected]
        new_inventory = [item for item in inventory if item.get("product_id") not in selected_ids]
        save_inventory(new_inventory)
        refresh_table()
        messagebox.showinfo("Removed", "Selected items have been removed from inventory.")

    Button(alert_frame, text="🔁 Refresh", command=refresh_table,
           bg="#2980b9", fg="white", padx=10, pady=5).pack(side=LEFT, padx=(0, 10))

    Button(alert_frame, text="🗑 Remove", command=archive_selected,
           bg="#c0392b", fg="white", padx=10, pady=5).pack(side=LEFT, padx=(0, 10))

    filter_option.trace_add("write", lambda *args: refresh_table())

    refresh_table()  # ✅ Ensures "7 Days" results shown by default
    return alert_frame
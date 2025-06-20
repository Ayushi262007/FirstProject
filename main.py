from tkinter import *
import sys
import subprocess  
from tkinter import messagebox  

from topbar import create_topbar
from leftbar import create_left_sidebar
from dashboard import create_dashboard
from add_product import create_add_product, create_edit_product_form  
from view_inventory import create_view_inventory
from storage import *
from purchase_request import create_purchase_request
from expiry_alert import create_expiry_alert
from warehouse import create_warehouse_module
from login import LoginRegisterApp
# Accept username from login
if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    username = "admin"

win = Tk()
win.title("Inventory Management System")
win.geometry("900x700")
win.configure(bg="#ecf0f1")

win.rowconfigure(1, weight=1)
win.columnconfigure(0, weight=0)
win.columnconfigure(1, weight=1)

main_content = Frame(win, bg="white")
main_content.grid(row=1, column=1, sticky="nsew")

# ✅ Ensure main_content expands properly
main_content.rowconfigure(0, weight=1)
main_content.columnconfigure(0, weight=1)

# ✅ Clear main content area
def clear_main_content():
    for widget in main_content.winfo_children():
        widget.destroy()

# ✅ Dashboard view
def show_dashboard():
    clear_main_content()
    create_dashboard(main_content, load_inventory)

# ✅ Add product
def show_add_product():
    clear_main_content()
    create_add_product(main_content)

# ✅ Edit product
def show_edit_product(product_id):
    clear_main_content()
    create_edit_product_form(main_content, product_id, back_callback=show_inventory)

# ✅ Inventory view
def show_inventory():
    clear_main_content()
    create_view_inventory(main_content, get_inventory_data=load_inventory, switch_to_module=handle_module_switch)

# ✅ Purchase requests
def show_purchase_requests():
    clear_main_content()
    create_purchase_request(main_content)

# ✅ Expiry alerts
def show_expiry_alerts():
    clear_main_content()
    create_expiry_alert(main_content)

# ✅ Warehouse view
def show_warehouse():
    clear_main_content()
    create_warehouse_module(main_content)

# ✅ Switch from profile → edit → back to dashboard
def switch_to_register(user_data):
    clear_main_content()

    def go_back_to_dashboard():
        show_dashboard()

    LoginRegisterApp(main_content, user_data=user_data, edit_mode=True, on_back=go_back_to_dashboard)

# ✅ Logout
def logout():  
    confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
    if confirm:
        win.destroy()
        subprocess.Popen(["python", "start.py"])  

# ✅ Handle module switch for inventory/edit
def handle_module_switch(module_name, *args):
    if module_name == "add_product":
        show_add_product()
    elif module_name == "edit_product" and args:
        show_edit_product(args[0])
    elif module_name == "inventory":
        show_inventory()

# ✅ Topbar with switch_to_register for profile edit
create_topbar(win, username, switch_to_register_callback=switch_to_register)

# ✅ Sidebar
create_left_sidebar(win, {
    "Dashboard": show_dashboard,
    "Add Product": show_add_product,
    "View Inventory": show_inventory,
    "Purchase Requests": show_purchase_requests,
    "Expiry Alerts": show_expiry_alerts,
    "Warehouses": show_warehouse,
    "Logout": logout,
})

# ✅ Default load
show_dashboard()
win.mainloop()









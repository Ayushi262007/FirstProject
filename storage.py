import json
import os

# File paths
INVENTORY_FILE = "products.json"
REQUESTS_FILE = "requests.json"
WAREHOUSE_FILE = "warehouses.json"  # ✅ NEW

# Generic JSON file helpers
def read_json_file(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"[Warning] {filename} is corrupted. Returning empty list.")
    return []

def write_json_file(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

# --------------------------
# Inventory Management
# --------------------------

def load_inventory():
    return read_json_file(INVENTORY_FILE)

def save_inventory(data):
    write_json_file(INVENTORY_FILE, data)

# --------------------------
# Purchase Request Management
# --------------------------

def load_requests():
    return read_json_file(REQUESTS_FILE)

def save_purchase_requests(data):
    write_json_file(REQUESTS_FILE, data)

# --------------------------
# Warehouse Management (NEW)
# --------------------------

def load_warehouses():
    return read_json_file(WAREHOUSE_FILE)

def save_warehouses(data):
    write_json_file(WAREHOUSE_FILE, data)

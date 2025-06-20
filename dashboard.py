# dashboard
from tkinter import *
from datetime import datetime
from storage import load_requests
import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

WAREHOUSE_FILE = "warehouse_data.json"

def is_expired(expiry_date_str):
    try:
        expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d")
        return expiry_date < datetime.now()
    except:
        return False

def create_performer_frame(parent, title, performers, fg_color):
    frame = Frame(parent, bg="#a5dbe9")
    container = Frame(frame, bg="#023c4b", highlightbackground="white", highlightthickness=2)
    container.pack(fill="both", expand=True, padx=10, pady=(30, 10))

    Label(container, text=title, bg="#023c4b", fg="white", font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

    for i, p in enumerate(performers):
        name = p.get("name", "N/A")
        qty = p.get("quantity", 0)
        row_frame = Frame(container, bg="#023c4b")
        row_frame.pack(anchor="w", padx=20, pady=5)
        Label(row_frame, text=f"{i+1}. {name}", bg="#023c4b", fg="white", font=("Segoe UI", 12, "bold")).pack(side="left")
        Label(row_frame, text=f" - Quantity: {qty}", bg="#023c4b", fg=fg_color, font=("Segoe UI", 12)).pack(side="left")

    return frame

def create_dashboard(parent, data_source):
    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)

    dashboard = Frame(parent, bg="#a5dbe9")
    dashboard.grid(row=0, column=0, sticky="nsew")

    for i in range(4):
        dashboard.rowconfigure(i, weight=1)
    for i in range(6):
        dashboard.columnconfigure(i, weight=1, uniform="card")

    inventory = data_source() if callable(data_source) else []

    total_products = len(inventory)
    low_stock_items = [p for p in inventory if p.get("quantity", 0) < 10]
    expired_items = [p for p in inventory if "expiry" in p and is_expired(p["expiry"])]
    total_quantity = sum(p.get("quantity", 0) for p in inventory)

    requests = load_requests()
    pending_requests = [r for r in requests if r.get("status", "").lower() == "pending"]

    total_warehouses = 0
    if os.path.exists(WAREHOUSE_FILE):
        try:
            with open(WAREHOUSE_FILE, "r") as file:
                warehouses = json.load(file)
                total_warehouses = len(warehouses)
        except Exception:
            total_warehouses = 0

    title = Label(dashboard, text="📊 Dashboard", bg="#a5dbe9", fg="#2c3e50", font=("Segoe UI", 22, "bold"))
    title.grid(row=0, column=0, columnspan=6, sticky="w", padx=20, pady=(20, 10))

    def create_card(row, column, title, value, bg_color):
        card = Frame(dashboard, bg=bg_color, width=180, height=130)
        card.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        card.grid_propagate(False)

        inner = Frame(card, bg=bg_color)
        inner.place(relx=0.5, rely=0.5, anchor="center")

        Label(inner, text=title, bg=bg_color, fg="white", font=("Segoe UI", 14, "bold")).pack()
        Label(inner, text=str(value), bg=bg_color, fg="white", font=("Segoe UI", 25, "bold")).pack(pady=5)

    create_card(1, 0, "Total Products", total_products, "#3498db")
    create_card(1, 1, "Low Stock", len(low_stock_items), "#e67e22")
    create_card(1, 2, "Expired Items", len(expired_items), "#e74c3c")
    create_card(1, 3, "Pending Requests", len(pending_requests), "#9b59b6")
    create_card(1, 4, "Total Warehouses", total_warehouses, "#16a085")
    create_card(1, 5, "Total Quantity", total_quantity, "#34495e")

    # Pie Chart
    chart_labels = ['Good Stock', 'Low Stock', 'Expired']
    good_items = total_products - len(low_stock_items) - len(expired_items)
    if good_items < 0:
        good_items = 0
    chart_values = [good_items, len(low_stock_items), len(expired_items)]
    chart_colors = ['#3498db', '#e67e22', '#e74c3c']
    explode = (0, 0, 0)

    filtered = [(l, v, c, e) for l, v, c, e in zip(chart_labels, chart_values, chart_colors, explode) if v > 0]
    if filtered:
        labels, values, colors, explodes = zip(*filtered)
    else:
        labels, values, colors, explodes = [], [], [], []

    fig, ax = plt.subplots(figsize=(7.8, 5.8), dpi=100)

    def make_autopct(values, labels):
        def custom_pct(pct):
            label = labels[custom_pct.index]
            custom_pct.index += 1
            return f'{label}\n{pct:.1f}%'
        custom_pct.index = 0
        return custom_pct

    if values:
        wedges, texts, autotexts = ax.pie(
            values,
            labels=None,
            autopct=make_autopct(values, labels),
            colors=colors,
            explode=explodes,
            startangle=90,
            counterclock=False,
            textprops=dict(color="#ffffff", fontsize=12)
        )
        ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=9,
                  title="Status", labelcolor="#2c3e50")
        ax.text(0, 0, f"Total\n{total_products}", ha='center', va='center', fontsize=12,
                weight='bold', color="#2c3e50")
    else:
        ax.text(0.5, 0.5, "No data to display", ha='center', va='center', fontsize=12, color="#2c3e50")
        ax.axis('off')

    ax.set_title("Inventory Status", fontsize=20, color="#2c3e50", weight="bold")
    ax.axis('equal')
    fig.tight_layout()

    chart_container = Frame(dashboard, bg="#a5dbe9", highlightbackground="#a5dbe9", highlightthickness=2)
    chart_container.grid(row=2, column=3, columnspan=100, rowspan=120, sticky="e", padx=(70, 50), pady=40)

    chart = FigureCanvasTkAgg(fig, chart_container)
    chart.draw()
    chart.get_tk_widget().pack()

    # Performer Data
    top_n = 3
    if inventory:
        sorted_inventory = sorted(inventory, key=lambda p: p.get("quantity", 0), reverse=True)
        top_performers = sorted_inventory[:top_n]
        least_performers = sorted_inventory[-top_n:]
    else:
        top_performers = [{"name": "N/A", "quantity": 0}] * 3
        least_performers = [{"name": "N/A", "quantity": 0}] * 3

    dashboard.rowconfigure(2, weight=2)
    dashboard.rowconfigure(3, weight=2)

    top_frame = create_performer_frame(dashboard, "🏆 Top Performers", top_performers, "#2980b9")
    top_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=20, pady=(10, 5))

    least_frame = create_performer_frame(dashboard, "🐢 Least Performers", least_performers, "#c0392b")
    least_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=20, pady=(0, 10))

    return dashboard






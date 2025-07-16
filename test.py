import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# -------------------------------
# SQLite Database Setup
conn = sqlite3.connect("nursery.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    address TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    description TEXT,
    sku TEXT,
    price REAL,
    cost_price REAL,
    quantity INTEGER,
    reorder_at INTEGER,
    supplier_id INTEGER,
    FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    total REAL,
    notes TEXT,
    date TEXT DEFAULT CURRENT_DATE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY(order_id) REFERENCES orders(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
)
""")

conn.commit()

# -------------------------------
# GUI Setup
root = tk.Tk()
root.title("Nursery Inventory Management")
root.geometry("950x600")

# -------------------------------
# Functions
def show_inventory():
    clear_frame()
    header_frame = tk.Frame(frame)
    header_frame.pack(fill="x", pady=5, padx=10)

    tk.Label(header_frame, text="Inventory", font=("Arial", 20)).pack(side="left")
    tk.Button(header_frame, text="Restock", bg="#4CAF50", fg="white", command=restock_product).pack(side="right", padx=5)
    tk.Button(header_frame, text="+ Add Product", bg="#4CAF50", fg="white", command=add_product).pack(side="right", padx=5)

    tree = ttk.Treeview(frame, columns=("Name", "Category", "SKU", "Price", "Stock", "Supplier"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
    tree.pack(expand=True, fill="both", padx=10, pady=10)

    rows = cursor.execute("""
        SELECT p.name, p.category, p.sku, p.price, p.quantity, s.name
        FROM products p LEFT JOIN suppliers s ON p.supplier_id = s.id
    """).fetchall()
    for row in rows:
        tree.insert("", tk.END, values=row)

    if not rows:
        tk.Label(frame, text="No products found.", fg="gray").pack(pady=20)

def show_suppliers():
    clear_frame()
    header_frame = tk.Frame(frame)
    header_frame.pack(fill="x", pady=5, padx=10)

    tk.Label(header_frame, text="Suppliers", font=("Arial", 20)).pack(side="left")
    tk.Button(header_frame, text="+ Add Supplier", bg="#4CAF50", fg="white", command=add_supplier).pack(side="right", padx=5)

    tree = ttk.Treeview(frame, columns=("Name", "Contact Person", "Email", "Phone", "Address"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
    tree.pack(expand=True, fill="both", padx=10, pady=10)

    rows = cursor.execute("SELECT name, contact_person, email, phone, address FROM suppliers").fetchall()
    for row in rows:
        tree.insert("", tk.END, values=row)

    if not rows:
        tk.Label(frame, text="No suppliers found.", fg="gray").pack(pady=20)

def show_orders():
    clear_frame()
    header_frame = tk.Frame(frame)
    header_frame.pack(fill="x", pady=5, padx=10)

    tk.Label(header_frame, text="Orders", font=("Arial", 20)).pack(side="left")
    tk.Button(header_frame, text="+ Create Order", bg="#4CAF50", fg="white", command=create_order).pack(side="right", padx=5)

    tree = ttk.Treeview(frame, columns=("ID", "Customer", "Date", "Total"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
    tree.pack(expand=True, fill="both", padx=10, pady=10)

    rows = cursor.execute("SELECT id, customer_name, date, total FROM orders").fetchall()
    for row in rows:
        tree.insert("", tk.END, values=row)

    if not rows:
        tk.Label(frame, text="No orders found.", fg="gray").pack(pady=20)

def clear_frame():
    for widget in frame.winfo_children():
        widget.destroy()

# -------------------------------
# Modals
def add_product():
    def save_product():
        supplier_name = supplier.get()
        supplier_id = None
        if supplier_name != "None":
            supplier_id = cursor.execute("SELECT id FROM suppliers WHERE name=?", (supplier_name,)).fetchone()
            if supplier_id:
                supplier_id = supplier_id[0]
        cursor.execute("""
            INSERT INTO products (name, category, description, sku, price, cost_price, quantity, reorder_at, supplier_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name.get(), category.get(), desc.get("1.0", tk.END), sku.get(), float(price.get()), float(cost.get()),
              int(quantity.get()), int(reorder.get()), supplier_id))
        conn.commit()
        top.destroy()
        show_inventory()

    top = tk.Toplevel(root)
    top.title("Add Product")
    tk.Label(top, text="Name").grid(row=0, column=0, sticky="e")
    name = tk.Entry(top); name.grid(row=0, column=1)
    tk.Label(top, text="Category").grid(row=1, column=0, sticky="e")
    category = tk.Entry(top); category.grid(row=1, column=1)
    tk.Label(top, text="Description").grid(row=2, column=0, sticky="e")
    desc = tk.Text(top, height=3, width=30); desc.grid(row=2, column=1)
    tk.Label(top, text="SKU").grid(row=3, column=0, sticky="e")
    sku = tk.Entry(top); sku.grid(row=3, column=1)
    tk.Label(top, text="Price").grid(row=4, column=0, sticky="e")
    price = tk.Entry(top); price.grid(row=4, column=1)
    tk.Label(top, text="Cost Price").grid(row=5, column=0, sticky="e")
    cost = tk.Entry(top); cost.grid(row=5, column=1)
    tk.Label(top, text="Quantity").grid(row=6, column=0, sticky="e")
    quantity = tk.Entry(top); quantity.grid(row=6, column=1)
    tk.Label(top, text="Reorder At").grid(row=7, column=0, sticky="e")
    reorder = tk.Entry(top); reorder.grid(row=7, column=1)
    tk.Label(top, text="Supplier").grid(row=8, column=0, sticky="e")
    supplier_names = ["None"] + [row[0] for row in cursor.execute("SELECT name FROM suppliers").fetchall()]
    supplier = ttk.Combobox(top, values=supplier_names)
    supplier.grid(row=8, column=1)
    tk.Button(top, text="Save", bg="#4CAF50", fg="white", command=save_product).grid(row=9, column=0, columnspan=2, pady=10)

def restock_product():
    def save_restock():
        product_name = product.get()
        if product_name != "":
            cursor.execute("UPDATE products SET quantity = quantity + ? WHERE name=?", (int(quantity.get()), product_name))
            conn.commit()
            top.destroy()
            show_inventory()

    top = tk.Toplevel(root)
    top.title("Restock Inventory")
    tk.Label(top, text="Product").grid(row=0, column=0, sticky="e")
    product_names = [row[0] for row in cursor.execute("SELECT name FROM products").fetchall()]
    product = ttk.Combobox(top, values=product_names)
    product.grid(row=0, column=1)
    tk.Label(top, text="Quantity to Add").grid(row=1, column=0, sticky="e")
    quantity = tk.Entry(top); quantity.grid(row=1, column=1)
    tk.Button(top, text="Restock", bg="#4CAF50", fg="white", command=save_restock).grid(row=2, column=0, columnspan=2, pady=10)

def create_order():
    def save_order():
        product_name = product.get()
        product_id = cursor.execute("SELECT id FROM products WHERE name=?", (product_name,)).fetchone()[0]
        total_price = cursor.execute("SELECT price FROM products WHERE id=?", (product_id,)).fetchone()[0] * int(quantity.get())
        cursor.execute("INSERT INTO orders (customer_name, total, notes) VALUES (?, ?, ?)",
                       (customer_name.get(), total_price, notes.get("1.0", tk.END)))
        order_id = cursor.lastrowid
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
                       (order_id, product_id, int(quantity.get())))
        cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id=?", (int(quantity.get()), product_id))
        conn.commit()
        top.destroy()
        show_orders()

    top = tk.Toplevel(root)
    top.title("Create New Order")
    tk.Label(top, text="Customer").grid(row=0, column=0, sticky="e")
    customer_name = tk.Entry(top); customer_name.grid(row=0, column=1)
    tk.Label(top, text="Product").grid(row=1, column=0, sticky="e")
    product_names = [row[0] for row in cursor.execute("SELECT name FROM products").fetchall()]
    product = ttk.Combobox(top, values=product_names)
    product.grid(row=1, column=1)
    tk.Label(top, text="Quantity").grid(row=2, column=0, sticky="e")
    quantity = tk.Entry(top); quantity.grid(row=2, column=1)
    tk.Label(top, text="Notes").grid(row=3, column=0, sticky="e")
    notes = tk.Text(top, height=3, width=30); notes.grid(row=3, column=1)
    tk.Button(top, text="Create Order", bg="#4CAF50", fg="white", command=save_order).grid(row=4, column=0, columnspan=2, pady=10)

def add_supplier():
    def save_supplier():
        cursor.execute("""
            INSERT INTO suppliers (name, contact_person, email, phone, address)
            VALUES (?, ?, ?, ?, ?)
        """, (name.get(), contact.get(), email.get(), phone.get(), address.get("1.0", tk.END)))
        conn.commit()
        top.destroy()
        show_suppliers()

    top = tk.Toplevel(root)
    top.title("Add Supplier")
    tk.Label(top, text="Company Name").grid(row=0, column=0, sticky="e")
    name = tk.Entry(top); name.grid(row=0, column=1)
    tk.Label(top, text="Contact Person").grid(row=1, column=0, sticky="e")
    contact = tk.Entry(top); contact.grid(row=1, column=1)
    tk.Label(top, text="Email").grid(row=2, column=0, sticky="e")
    email = tk.Entry(top); email.grid(row=2, column=1)
    tk.Label(top, text="Phone").grid(row=3, column=0, sticky="e")
    phone = tk.Entry(top); phone.grid(row=3, column=1)
    tk.Label(top, text="Address").grid(row=4, column=0, sticky="e")
    address = tk.Text(top, height=3, width=30); address.grid(row=4, column=1)
    tk.Button(top, text="Save", bg="#4CAF50", fg="white", command=save_supplier).grid(row=5, column=0, columnspan=2, pady=10)

# -------------------------------
# Navbar
menu = tk.Frame(root, bg="#f0f0f0")
tk.Button(menu, text="Inventory", width=20, command=show_inventory).pack(side="left")
tk.Button(menu, text="Orders", width=20, command=show_orders).pack(side="left")
tk.Button(menu, text="Suppliers", width=20, command=show_suppliers).pack(side="left")
menu.pack(fill="x")

frame = tk.Frame(root)
frame.pack(expand=True, fill="both")

# -------------------------------
# Start with Inventory Page
show_inventory()

root.mainloop()

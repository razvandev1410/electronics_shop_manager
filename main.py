import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import mysql.connector
import numpy as np
import matplotlib.pyplot as plot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def connect_to_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="razvandata",
        database="schema"
    )

prices_ron = []

def update_tree_columns(columns, headings):
    tree.delete(*tree.get_children())
    tree.configure(columns=columns)
    for col, heading in zip(columns, headings):
        tree.heading(col, text=heading)
        tree.column(col, width=100)

def view_products():
    for item in tree.get_children():
        tree.delete(item)

    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Produs")
        rows = cursor.fetchall()

        update_tree_columns(["model", "fabricant", "categorie", "pret", "moneda"], ["Model", "Manufacturer", "Category", "Price", "Currency"])

        for row in rows:
            tree.insert("", tk.END, values=row)

        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

def add_product():
    model = simpledialog.askinteger("Add Product", "Enter model number:")
    if model is None: return

    fabricant = simpledialog.askstring("Add Product", "Enter manufacturer name:")
    categorie = simpledialog.askstring("Add Product", "Enter category (PC / LAPTOP / IMPRIMANTA):")
    pret = simpledialog.askfloat("Add Product", "Enter price:")
    moneda = simpledialog.askstring("Add Product", "Enter currency (EUR / RON):")

    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Produs (model, fabricant, categorie, pret, moneda) VALUES (%s, %s, %s, %s, %s)",
            (model, fabricant, categorie.upper(), pret, moneda.upper())
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Product added successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

def delete_product():
    global prices_ron
    model = simpledialog.askinteger("Delete Product", "Enter model number to delete:")
    if model is None: return

    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.execute("SELECT pret, moneda FROM Produs WHERE model = %s", (model,))
        product = cursor.fetchone()

        if product:
            price, currency = product
            price = float(price)
            if currency == "EUR":
                price = price * 4.95
            prices_ron.append(price)
            cursor.execute("DELETE FROM PC WHERE model = %s", (model,))
            cursor.execute("DELETE FROM Laptop WHERE model = %s", (model,))
            cursor.execute("DELETE FROM Imprimanta WHERE model = %s", (model,))
            cursor.execute("DELETE FROM Produs WHERE model = %s", (model,))
            conn.commit()
            messagebox.showinfo("Success", "Product deleted successfully!")
        else:
            messagebox.showinfo("Error", "No product with this model exists!")
        conn.close()

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

def modify_price():
    model = simpledialog.askinteger("Modify Price", "Enter model:")
    if model is None: return

    new_price = simpledialog.askfloat("Modify Price", "Enter new price:")

    if new_price is None: return

    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE Produs SET pret = %s WHERE model = %s", (new_price, model))
        conn.commit()
        conn.close()

        if cursor.rowcount > 0:
            messagebox.showinfo("Success", "Price updated successfully!")
        else:
            messagebox.showinfo("Not Found", "No product found with the given model.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

def see_statistics():
    global prices_ron
    if not prices_ron:
        messagebox.showinfo("Error", "No products have been sold yet.")
        return

    x = np.arange(1, len(prices_ron) + 1)
    y = np.array(prices_ron)

    # linear reg
    coefficients = np.polyfit(x, y, 1)
    regression_line = np.polyval(coefficients, x)

    figure, ax = plot.subplots()
    ax.plot(x, y, 'bo-', label="Item Sold")
    ax.plot(x, regression_line, 'r--', label="Linear Regression")
    ax.set_title("Income analysis")
    ax.set_xlabel("Units")
    ax.set_ylabel("Price (RON)")
    ax.legend()

    stats_window = tk.Toplevel(app)
    stats_window.title("Statistics")
    canvas = FigureCanvasTkAgg(figure, master=stats_window)
    canvas.get_tk_widget().pack()
    canvas.draw()

def sort_pcs(option):
    for item in tree.get_children():
        tree.delete(item)

    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        if option == "Sort by price in RON":
            update_tree_columns(["model", "fabricant", "categorie", "pret"],["Model", "Manufacturer", "Category", "Price"])
            cursor.execute("""
                SELECT Produs.model, fabricant, categorie, 
                    CASE 
                        WHEN moneda = 'EUR' THEN pret * 4.95 
                        ELSE pret 
                    END 
                        AS price_in_ron, "RON"
                FROM Produs
                JOIN PC ON Produs.model = PC.model
                ORDER BY price_in_ron ASC
            """)
        elif option == "Sort by speed decreasingly":
            update_tree_columns(["model", "fabricant", "categorie", "pret", "moneda", "ram", "viteza"],["Model", "Manufacturer", "Category", "Price", "Currency", "Memory", "Speed"])
            cursor.execute("""
                SELECT Produs.model, fabricant, categorie, pret, moneda, PC.ram, PC.viteza
                FROM Produs
                JOIN PC ON Produs.model = PC.model
                ORDER BY PC.viteza DESC
            """)
        elif option == "Sort by memory decreasingly":
            update_tree_columns(["model", "fabricant", "categorie", "pret", "moneda", "ram", "viteza"],["Model", "Manufacturer", "Category", "Price", "Currency", "Memory", "Speed"])
            cursor.execute("""
                SELECT Produs.model, fabricant, categorie, pret, moneda, PC.ram, PC.viteza
                FROM Produs
                JOIN PC ON Produs.model = PC.model
                ORDER BY PC.ram DESC
            """)

        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", tk.END, values=row)

        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

def sort_laptops(option):
    for item in tree.get_children():
        tree.delete(item)

    try:
        conn = connect_to_db()
        cursor = conn.cursor()


        if option == "Sort by price in RON":
            update_tree_columns(["model", "fabricant", "categorie"],["Model", "Manufacturer", "Category"])
            cursor.execute("""
                SELECT Produs.model, fabricant, categorie, 
                    CASE 
                        WHEN moneda = 'EUR' THEN pret * 4.95 
                        ELSE pret 
                    END 
                        AS price_in_ron, "RON"
                FROM Produs
                JOIN Laptop ON Produs.model = Laptop.model
                ORDER BY price_in_ron ASC
            """)
        elif option == "Sort by speed decreasingly":
            update_tree_columns(["model", "fabricant", "categorie", "pret", "moneda", "ram", "viteza"],["Model", "Manufacturer", "Category", "Price", "Currency", "Memory", "Speed"])
            cursor.execute("""
                SELECT Produs.model, fabricant, categorie, pret, moneda, Laptop.ram, Laptop.viteza
                FROM Produs
                JOIN Laptop ON Produs.model = Laptop.model
                ORDER BY Laptop.viteza DESC
            """)
        elif option == "Sort by memory decreasingly":
            update_tree_columns(["model", "fabricant", "categorie", "pret", "moneda", "ram", "viteza"],["Model", "Manufacturer", "Category", "Price", "Currency", "Memory", "Speed"])
            cursor.execute("""
                SELECT Produs.model, fabricant, categorie, pret, moneda, Laptop.ram, Laptop.viteza
                FROM Produs
                JOIN Laptop ON Produs.model = Laptop.model
                ORDER BY Laptop.ram DESC
            """)

        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", tk.END, values=row)

        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

def sort_printers(option):
    for item in tree.get_children():
        tree.delete(item)

    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        if option == "Sort by price in RON":
            update_tree_columns(["model", "fabricant", "categorie"],["Model", "Manufacturer", "Category"])
            cursor.execute("""
                SELECT Produs.model, fabricant, categorie, 
                    CASE 
                        WHEN moneda = 'EUR' THEN pret * 4.95 
                        ELSE pret 
                    END 
                        AS price_in_ron, "RON"
                FROM Produs
                JOIN Imprimanta ON Produs.model = Imprimanta.model
                ORDER BY price_in_ron ASC
            """)

        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", tk.END, values=row)

        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

def on_pcs_sort(event):
    option = pcs_combobox.get()
    sort_pcs(option)

def on_laptops_sort(event):
    option = laptops_combobox.get()
    sort_laptops(option)

def on_printers_sort(event):
    option = printers_combobox.get()
    sort_printers(option)

#3a
def show_laser_printers():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Imprimanta WHERE tip = 'laser' ORDER BY culoare DESC")
        rows = cursor.fetchall()
        conn.close()

        update_tree_columns(["model", "culoare", "tip"], ["Model", "Color", "Type"])
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert("", tk.END, values=row)

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

#3b
def show_large_screen_laptops():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        size = simpledialog.askfloat("Enter size", "Enter the desired size:")
        cursor.execute("""SELECT * 
        FROM Laptop
        WHERE ecran > %s
        ORDER BY hd ASC, viteza DESC""", (size, ))
        rows = cursor.fetchall()
        conn.close()

        update_tree_columns(["model", "viteza", "ram", "hd", "ecran"], ["Model", "Speed", "RAM", "HD", "Screen Size"])
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert("", tk.END, values=row)

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

#4a
def show_hp_products():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.model, 
                p.categorie, 
                l.viteza AS viteza_laptop, 
                l.ram AS ram_laptop, 
                l.hd AS hd_laptop, 
                pc.viteza AS viteza_pc, 
                pc.ram AS ram_pc, 
                pc.hd AS hd_pc, 
                p.pret, 
                p.moneda
            FROM 
                Produs p
            LEFT JOIN Laptop l ON p.model = l.model AND p.categorie = 'LAPTOP'
            LEFT JOIN PC pc ON p.model = pc.model AND p.categorie = 'PC'
            WHERE 
                p.fabricant = 'HP' AND p.categorie IN ('LAPTOP', 'PC')
            ORDER BY 
                p.categorie ASC, 
                p.moneda ASC, 
                p.pret ASC
        """)
        rows = cursor.fetchall()
        conn.close()

        update_tree_columns(["model", "categorie", "viteza_laptop", "ram_laptop", "hd_laptop", "viteza_pc", "ram_pc", "hd_pc", "pret", "moneda"], ["Model", "Category", "Laptop Speed", "Laptop RAM", "Laptop HD","PC Speed", "PC RAM", "PC HD", "Price", "Currency"])
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert("", tk.END, values=row)

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
#4b
def show_similar_printers():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                i1.model AS model1, 
                i2.model AS model2
            FROM Imprimanta i1
            JOIN Imprimanta i2 ON i1.tip = i2.tip 
            JOIN Produs p1 ON i1.model = p1.model
            JOIN Produs p2 ON i2.model = p2.model
            WHERE p1.fabricant <> p2.fabricant AND i1.model < i2.model
        """)
        rows = cursor.fetchall()
        conn.close()

        update_tree_columns(["model1", "model2"], ["Model 1", "Model 2"])
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert("", tk.END, values=row)

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
#5a
def show_fastest_laptops():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.fabricant, 
                l.viteza
            FROM 
                Laptop l
            JOIN 
                Produs p ON l.model = p.model
            WHERE l.viteza >= ALL (SELECT l2.viteza FROM Laptop l2)
        """)
        rows = cursor.fetchall()
        conn.close()

        update_tree_columns(["fabricant", "viteza"], ["Manufacturer", "Speed"])
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert("", tk.END, values=row)

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
#5b
def show_similar_pcs():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        pret = simpledialog.askinteger("Enter model", "Enter the desired PC model:")
        cursor.execute("""
            SELECT 
                p.fabricant, 
                p.pret, 
                p.moneda
            FROM 
                PC pc
            JOIN 
                Produs p ON pc.model = p.model
            WHERE 
                (pc.viteza, pc.ram, pc.hd) IN (
                    SELECT 
                        pc2.viteza, pc2.ram, pc2.hd
                    FROM 
                        PC pc2
                    WHERE 
                        pc2.model = %s
                )
        """, (pret,))
        rows = cursor.fetchall()
        conn.close()

        update_tree_columns(["fabricant", "pret", "moneda"], ["Manufacturer", "Price", "Currency"])
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert("", tk.END, values=row)

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
#6a
def show_max_speed_laptop():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""CALL GetMaxSpeedLaptop()""")
        rows = cursor.fetchall()
        conn.close()

        update_tree_columns(["fabricant", "viteza"], ["Manufacturer", "Frequency"])
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert("", tk.END, values=row)

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
#6b
def show_cheapest_printer_stats():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                i.tip, 
                p.moneda, 
                MIN(p.pret) AS pret_minim, 
                AVG(p.pret) AS pret_mediu, 
                MAX(p.pret) AS pret_maxim
            FROM 
                Imprimanta i
            JOIN 
                Produs p ON i.model = p.model
            GROUP BY 
                i.tip, 
                p.moneda
        """)
        rows = cursor.fetchall()
        conn.close()

        update_tree_columns(["tip", "moneda", "pret_minim", "pret_mediu", "pret_maxim"],["Type", "Currency", "Min Price", "Avg Price", "Max Price"])
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert("", tk.END, values=row)

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")


app = tk.Tk()
app.title("Raz's Device House")
app.geometry("800x600")

button_frame = tk.Frame(app)
button_frame.pack(pady=10)

combo_frame = tk.Frame(app)
combo_frame.pack(pady=10)

view_button = tk.Button(button_frame, text="View Products", command=view_products)
add_button = tk.Button(button_frame, text="Add Product", command=add_product)
delete_button = tk.Button(button_frame, text="Delete Product", command=delete_product)
modify_button = tk.Button(button_frame, text="Modify Price", command=modify_price)
stats_button = tk.Button(button_frame, text="See Statistic", command=see_statistics)

view_button.pack(side=tk.LEFT, padx=5)
add_button.pack(side=tk.LEFT, padx=5)
delete_button.pack(side=tk.LEFT, padx=5)
modify_button.pack(side=tk.LEFT, padx=5)
stats_button.pack(side=tk.LEFT, padx=5)

bottom_button_frame = tk.Frame(app)
bottom_button_frame.pack(side=tk.BOTTOM, pady=10)

laser_printers_button = tk.Button(bottom_button_frame, text="Laser Printers", command=show_laser_printers)
large_screen_laptops_button = tk.Button(bottom_button_frame, text="Large Screen Laptops", command=show_large_screen_laptops)
hp_products_button = tk.Button(bottom_button_frame, text="HP Products", command=show_hp_products)
similar_printers_button = tk.Button(bottom_button_frame, text="Similar Printers", command=show_similar_printers)
fastest_laptops_button = tk.Button(bottom_button_frame, text="Fastest Laptops", command=show_fastest_laptops)
similar_pcs_button = tk.Button(bottom_button_frame, text="Similar PCs", command=show_similar_pcs)
cheapest_printer_stats_button = tk.Button(bottom_button_frame, text="Cheapest Printer Details", command=show_cheapest_printer_stats)
max_speed_laptop_button = tk.Button(bottom_button_frame, text="Max Speed Laptops", command=show_max_speed_laptop)

laser_printers_button.pack(side=tk.LEFT, padx=2)
large_screen_laptops_button.pack(side=tk.LEFT, padx=2)
hp_products_button.pack(side=tk.LEFT, padx=2)
similar_printers_button.pack(side=tk.LEFT, padx=2)
fastest_laptops_button.pack(side=tk.LEFT, padx=2)
similar_pcs_button.pack(side=tk.LEFT, padx=2)
cheapest_printer_stats_button.pack(side=tk.LEFT, padx=2)
max_speed_laptop_button.pack(side=tk.LEFT, padx=2)

columns = ("model", "fabricant", "categorie", "pret", "moneda", "ram", "viteza")
tree = ttk.Treeview(app, columns=columns, show="headings", height=15)

tree.heading("model", text="Model")
tree.heading("fabricant", text="Manufacturer")
tree.heading("categorie", text="Category")
tree.heading("pret", text="Price")
tree.heading("moneda", text="Currency")
tree.heading("ram", text="RAM")
tree.heading("viteza", text="Frequency")

tree.column("model", width=100)
tree.column("fabricant", width=150)
tree.column("categorie", width=120)
tree.column("pret", width=100)
tree.column("moneda", width=100)
tree.column("ram", width=100)
tree.column("viteza", width=100)


tree.pack(pady=20)

pcs_label = ttk.Label(combo_frame, text="PCs:")
pcs_label.grid(row=0, column=0, padx=5)
pcs_combobox = ttk.Combobox(combo_frame, values=["Sort by price in RON", "Sort by speed decreasingly", "Sort by memory decreasingly"])
pcs_combobox.set("")
pcs_combobox.grid(row=0, column=1, padx=5)
pcs_combobox.bind("<<ComboboxSelected>>", on_pcs_sort)

laptops_label = ttk.Label(combo_frame, text="Laptops:")
laptops_label.grid(row=1, column=0, padx=5)
laptops_combobox = ttk.Combobox(combo_frame, values=["Sort by price in RON", "Sort by speed decreasingly", "Sort by memory decreasingly"])
laptops_combobox.set("")
laptops_combobox.grid(row=1, column=1, padx=5)
laptops_combobox.bind("<<ComboboxSelected>>", on_laptops_sort)

printers_label = ttk.Label(combo_frame, text="Printers:")
printers_label.grid(row=2, column=0, padx=5)
printers_combobox = ttk.Combobox(combo_frame, values=["Sort by price in RON"])
printers_combobox.set("")
printers_combobox.grid(row=2, column=1, padx=5)
printers_combobox.bind("<<ComboboxSelected>>", on_printers_sort)


app.mainloop()

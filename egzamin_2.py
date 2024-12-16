import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime

# Підключення до бази даних SQLite
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

# Створення таблиць
cursor.execute('''
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    date TEXT,
    category_id INTEGER,
    amount REAL,
    FOREIGN KEY (category_id) REFERENCES categories(id)
)
''')
conn.commit()

# Функції для роботи з базою даних
def add_category(name):
    try:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
        messagebox.showinfo("Успіх", "Категорія додана!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Помилка", "Категорія вже існує.")

def delete_category(name):
    cursor.execute("DELETE FROM categories WHERE name = ?", (name,))
    conn.commit()
    messagebox.showinfo("Успіх", "Категорію видалено!")

def add_expense(name, date, category, amount):
    cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
    category_id = cursor.fetchone()
    if category_id:
        cursor.execute("INSERT INTO expenses (name, date, category_id, amount) VALUES (?, ?, ?, ?)",
                       (name, date, category_id[0], amount))
        conn.commit()
        messagebox.showinfo("Успіх", "Витрата додана!")
    else:
        messagebox.showerror("Помилка", "Категорія не знайдена!")

def load_categories():
    cursor.execute("SELECT name FROM categories")
    return [row[0] for row in cursor.fetchall()]

def generate_report_by_date(date):
    cursor.execute("SELECT name, amount FROM expenses WHERE date = ?", (date,))
    return cursor.fetchall()

def generate_report_by_category(category):
    cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
    category_id = cursor.fetchone()
    if category_id:
        cursor.execute("SELECT name, amount FROM expenses WHERE category_id = ?", (category_id[0],))
        return cursor.fetchall()
    return []

def max_expense_by_category():
    cursor.execute('''
        SELECT categories.name, MAX(expenses.amount) FROM expenses
        JOIN categories ON expenses.category_id = categories.id
        GROUP BY categories.name
    ''')
    return cursor.fetchall()

def min_expense_by_category():
    cursor.execute('''
        SELECT categories.name, MIN(expenses.amount) FROM expenses
        JOIN categories ON expenses.category_id = categories.id
        GROUP BY categories.name
    ''')
    return cursor.fetchall()

def show_all_expenses():
    cursor.execute('''
        SELECT expenses.id, expenses.name, expenses.date, categories.name, expenses.amount
        FROM expenses
        JOIN categories ON expenses.category_id = categories.id
    ''')
    expenses = cursor.fetchall()
    report_text.delete(1.0, tk.END)
    for expense_id, name, date, category, amount in expenses:
        report_text.insert(tk.END, f"ID: {expense_id} | {date} - {name} ({category}): {amount} грн\n")

def delete_selected_expense():
    try:
        expense_id = int(expense_id_entry.get())
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        messagebox.showinfo("Успіх", "Витрату видалено!")
        show_all_expenses()  # Оновлюємо список витрат після видалення
    except ValueError:
        messagebox.showerror("Помилка", "Введіть коректний ID витрати.")
    except sqlite3.Error as e:
        messagebox.showerror("Помилка", f"Сталася помилка: {e}")

# Інтерфейс програми
root = tk.Tk()
root.title("Облік витрат")

# Додавання категорії
def add_category_ui():
    name = category_entry.get()
    add_category(name)
    category_entry.delete(0, tk.END)
    update_categories()

def delete_category_ui():
    name = category_entry.get()
    delete_category(name)
    category_entry.delete(0, tk.END)
    update_categories()

def update_categories():
    categories = load_categories()
    category_combobox["values"] = categories
    report_category_combobox["values"] = categories

# Додавання витрати
def add_expense_ui():
    name = expense_name_entry.get()
    date = expense_date_entry.get()
    category = category_combobox.get()
    try:
        amount = float(expense_amount_entry.get())
        add_expense(name, date, category, amount)
        expense_name_entry.delete(0, tk.END)
        expense_date_entry.delete(0, tk.END)
        expense_amount_entry.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Помилка", "Введіть коректну суму витрати.")

# Відображення звітів
# звіт по даті
def show_report_by_date():
    date = report_date_entry.get()
    report = generate_report_by_date(date)
    report_text.delete(1.0, tk.END)
    for item in report:
        report_text.insert(tk.END, f"{item[0]} - {item[1]} грн\n")

def show_report_by_category():
    category = report_category_combobox.get()
    report = generate_report_by_category(category)
    report_text.delete(1.0, tk.END)
    for item in report:
        report_text.insert(tk.END, f"{item[0]} - {item[1]} грн\n")
# звіт максимальна  витрата
def show_max_expense_by_category():
    report = max_expense_by_category()
    report_text.delete(1.0, tk.END)
    for item in report:
        report_text.insert(tk.END, f"{item[0]} - Максимальна витрата: {item[1]} грн\n")
# звіт мінімальна витрата
def show_min_expense_by_category():
    report = min_expense_by_category()
    report_text.delete(1.0, tk.END)
    for item in report:
        report_text.insert(tk.END, f"{item[0]} - Мінімальна витрата: {item[1]} грн\n")

# Елементи інтерфейсу
# Додавання категорії
tk.Label(root, text="Категорія").grid(row=0, column=0)
category_entry = tk.Entry(root)
category_entry.grid(row=0, column=1)
tk.Button(root, text="Додати", command=add_category_ui).grid(row=0, column=2)
tk.Button(root, text="Видалити", command=delete_category_ui).grid(row=0, column=3)

# Додавання витрати
tk.Label(root, text="Назва витрати").grid(row=1, column=0)
expense_name_entry = tk.Entry(root)
expense_name_entry.grid(row=1, column=1)

tk.Label(root, text="Дата (YYYY-MM-DD)").grid(row=2, column=0)
expense_date_entry = tk.Entry(root)
expense_date_entry.grid(row=2, column=1)

tk.Label(root, text="Категорія").grid(row=3, column=0)
category_combobox = ttk.Combobox(root)
category_combobox.grid(row=3, column=1)

tk.Label(root, text="Сума").grid(row=4, column=0)
expense_amount_entry = tk.Entry(root)
expense_amount_entry.grid(row=4, column=1)

tk.Button(root, text="Додати витрату", command=add_expense_ui).grid(row=5, column=1)

# Звіти
tk.Label(root, text="Дата звіту (YYYY-MM-DD)").grid(row=6, column=0)
report_date_entry = tk.Entry(root)
report_date_entry.grid(row=6, column=1)
tk.Button(root, text="Звіт за датою", command=show_report_by_date).grid(row=6, column=2)

tk.Label(root, text="Категорія звіту").grid(row=7, column=0)
report_category_combobox = ttk.Combobox(root)
report_category_combobox.grid(row=7, column=1)
tk.Button(root, text="Звіт за категорією", command=show_report_by_category).grid(row=7, column=2)

tk.Button(root, text="Максимальна витрата за категоріями", command=show_max_expense_by_category).grid(row=8, column=0)
tk.Button(root, text="Мінімальна витрата за категоріями", command=show_min_expense_by_category).grid(row=8, column=1)

# Кнопка для перегляду всіх витрат
tk.Button(root, text="Весь список витрат", command=show_all_expenses).grid(row=9, column=0, columnspan=2)

# Поле для введення ID витрати для видалення
tk.Label(root, text="ID витрати для видалення").grid(row=10, column=0)
expense_id_entry = tk.Entry(root)
expense_id_entry.grid(row=10, column=1)
tk.Button(root, text="Видалити витрату", command=delete_selected_expense).grid(row=10, column=2)

# Поле для виведення звітів
report_text = tk.Text(root, height=10, width=50)
report_text.grid(row=11, column=0, columnspan=3)

# Оновлення списку категорій
update_categories()

root.mainloop()

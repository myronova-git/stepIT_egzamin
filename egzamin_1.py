import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import sqlite3
from datetime import datetime

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Учет расходов")
        self.root.geometry('700x400')

        # Создаем или открываем базу данных
        self.db_connection = sqlite3.connect("expenses.db")
        self.db_cursor = self.db_connection.cursor()

        # Создаем таблицы, если они не существуют
        self.create_tables()

        # Заголовок
        title_label = tk.Label(root, text="УЧЕТ РАСХОДОВ", font=("Helvetica", 16, "bold"))
        title_label.pack()

        # Кнопки
        self.add_category_button = tk.Button(root, text="ДОБАВИТЬ КАТЕГОРИЮ", font=("Helvetica", 14, "bold"), bg="green", fg="white", command=self.add_category)
        self.add_category_button.pack(fill=tk.BOTH, padx=10, pady=5)

        self.add_expense_button = tk.Button(root, text="ДОБАВИТЬ РАСХОД", font=("Helvetica", 14, "bold"), bg="green",
                                            fg="white", command=self.add_expense)
        self.add_expense_button.pack(fill=tk.BOTH, padx=10, pady=5)

        self.list_categories_button = tk.Button(root, text="СПИСОК КАТЕГОРИЙ", font=("Helvetica", 14, "bold"), bg="green", fg="white", command=self.list_categories)
        self.list_categories_button.pack(fill=tk.BOTH, padx=10, pady=5)

        self.generate_report_button = tk.Button(root, text="СОЗДАТЬ ОТЧЕТ", font=("Helvetica", 14, "bold"), bg="green", fg="white", command=self.generate_report)
        self.generate_report_button.pack(fill=tk.BOTH, padx=10, pady=5)

        self.save_to_file_button = tk.Button(root, text="СОХРАНИТЬ В ФАЙЛ", font=("Helvetica", 14, "bold"), bg="green", fg="white", command=self.save_to_file)
        self.save_to_file_button.pack(fill=tk.BOTH, padx=10, pady=5)

        self.load_from_file_button = tk.Button(root, text="ЗАГРУЗИТЬ ИЗ ФАЙЛА", font=("Helvetica", 14, "bold"), bg="green", fg="white", command=self.load_from_file)
        self.load_from_file_button.pack(fill=tk.BOTH, padx=10, pady=5)

        self.delete_category_button = tk.Button(root, text="УДАЛИТЬ КАТЕГОРИЮ", font=("Helvetica", 14, "bold"),
                                                bg="red", fg="white", command=self.delete_category)
        self.delete_category_button.pack(fill=tk.BOTH, padx=10, pady=5)

    def create_tables(self):
        """Создаем таблицы для категорий и расходов, если они не существуют"""
        self.db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )""")

        self.db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )""")
        self.db_connection.commit()

    def add_category(self):
        """Добавление новой категории"""
        category = simpledialog.askstring("Категория", "Введите название категории:")
        if category:
            self.db_cursor.execute("INSERT INTO categories (name) VALUES (?)", (category,))
            self.db_connection.commit()
            messagebox.showinfo("Успех", f"Категория '{category}' добавлена.")

    def delete_category(self):
        """Удаление категории"""
        category = simpledialog.askstring("Категория", "Введите название категории для удаления:")
        self.db_cursor.execute("SELECT * FROM categories WHERE name = ?", (category,))
        category_row = self.db_cursor.fetchone()
        if category_row:
            self.db_cursor.execute("DELETE FROM categories WHERE name = ?", (category,))
            self.db_connection.commit()
            messagebox.showinfo("Успех", f"Категория '{category}' удалена.")
        else:
            messagebox.showerror("Ошибка", f"Категория '{category}' не найдена.")

    def list_categories(self):
        """Отображение списка категорий"""
        self.db_cursor.execute("SELECT name FROM categories")
        categories = self.db_cursor.fetchall()
        if categories:
            categories_str = "\n".join([category[0] for category in categories])
            messagebox.showinfo("Категории", categories_str)
        else:
            messagebox.showinfo("Категории", "Категории не найдены.")

    def add_expense(self):
        """Добавление нового расхода"""
        category = simpledialog.askstring("Категория", "Введите название существующей категории:")
        self.db_cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
        category_row = self.db_cursor.fetchone()
        if not category_row:
            messagebox.showerror("Ошибка", f"Категория '{category}' не найдена.")
            return

        date = simpledialog.askstring("Дата", "Введите дату (ГГГГ-ММ-ДД):")
        name = simpledialog.askstring("Название", "Введите название расхода:")
        amount = simpledialog.askfloat("Сумма", "Введите сумму расхода:")
        if date and name and amount:
            category_id = category_row[0]
            self.db_cursor.execute("INSERT INTO expenses (category_id, name, amount, date) VALUES (?, ?, ?, ?)",
                                   (category_id, name, amount, date))
            self.db_connection.commit()
            messagebox.showinfo("Успех", f"Расход '{name}' добавлен.")

    def generate_report(self):
        """Генерация отчета по расходам"""
        self.db_cursor.execute("""
        SELECT e.name, e.amount, e.date, c.name
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        """)
        expenses = self.db_cursor.fetchall()
        if not expenses:
            messagebox.showinfo("Отчет", "Расходов не обнаружено.")
            return

        max_expense = max(expenses, key=lambda x: x[1])
        min_expense = min(expenses, key=lambda x: x[1])
        total_expense = sum(expense[1] for expense in expenses)

        report_str = (
            f"Максимальный расход: {max_expense[0]} - {max_expense[1]} (Категория: {max_expense[3]}, Дата: {max_expense[2]})\n"
            f"Минимальный расход: {min_expense[0]} - {min_expense[1]} (Категория: {min_expense[3]}, Дата: {min_expense[2]})\n"
            f"Общий расход: {total_expense}\n"
        )

        messagebox.showinfo("Отчет", report_str)

    def save_to_file(self):
        """Сохранение данных в файл (не используется с базой данных)"""
        messagebox.showinfo("Информация", "Данные уже сохранены в базе данных.")

    def load_from_file(self):
        """Загрузка данных из файла (не используется с базой данных)"""
        messagebox.showinfo("Информация", "Данные уже загружены из базы данных.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()

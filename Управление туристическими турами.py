import tkinter as tk
from tkinter import ttk, messagebox
import json
import os


class TourManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Управление туристическими турами")
        self.root.geometry("800x550")

        self.data_file = "tours_data.json"
        self.tours = self.load_data()
        self.current_edit_index = None

        self.create_widgets()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []

    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.tours, f, ensure_ascii=False, indent=4)

    def create_widgets(self):
        input_frame = ttk.LabelFrame(self.root, text="Данные тура", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        fields = [
            ("Название тура:", "name_entry"),
            ("Страна:", "country_entry"),
            ("Город:", "city_entry"),
            ("Дата начала:", "start_date_entry"),
            ("Дата окончания:", "end_date_entry"),
            ("Цена ₽:", "price_entry")
        ]

        for i, (label_text, attr_name) in enumerate(fields):
            ttk.Label(input_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=2)
            entry = ttk.Entry(input_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=2)
            setattr(self, attr_name, entry)

        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Добавить тур", command=self.add_tour).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Сохранить изменения", command=self.save_edited_tour).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить", command=self.clear_fields).pack(side=tk.LEFT, padx=5)

        self.tree_frame = ttk.LabelFrame(self.root, text="Список туров", padding=10)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("name", "country", "city", "start_date", "end_date", "price")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")

        self.tree.heading("name", text="Название")
        self.tree.heading("country", text="Страна")
        self.tree.heading("city", text="Город")
        self.tree.heading("start_date", text="Дата начала")
        self.tree.heading("end_date", text="Дата окончания")
        self.tree.heading("price", text="Цена ₽")

        self.tree.column("name", width=150)
        self.tree.column("country", width=100)
        self.tree.column("city", width=100)
        self.tree.column("start_date", width=100)
        self.tree.column("end_date", width=100)
        self.tree.column("price", width=80)

        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        tree_button_frame = ttk.Frame(self.tree_frame)
        tree_button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(tree_button_frame, text="Удалить выбранное", command=self.delete_tour).pack(side=tk.LEFT, padx=5)
        ttk.Button(tree_button_frame, text="Обновить список", command=self.update_tree).pack(side=tk.LEFT, padx=5)

        self.update_tree()

    def on_double_click(self, event):
        self.edit_selected_tour()

    def on_tree_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            self.current_edit_index = self.tree.index(selected_item)

    def add_tour(self):
        tour_data = self.get_tour_data_from_entries()
        if not tour_data:
            return

        self.tours.append(tour_data)
        self.save_data()
        self.update_tree()
        self.clear_fields()
        messagebox.showinfo("Успех", "Тур успешно добавлен!")

    def save_edited_tour(self):
        if self.current_edit_index is None:
            messagebox.showwarning("Ошибка", "Сначала выберите тур для редактирования")
            return

        tour_data = self.get_tour_data_from_entries()
        if not tour_data:
            return

        self.tours[self.current_edit_index] = tour_data
        self.save_data()
        self.update_tree()
        messagebox.showinfo("Успех", "Изменения сохранены!")

    def get_tour_data_from_entries(self):
        name = self.name_entry.get().strip()
        country = self.country_entry.get().strip()
        city = self.city_entry.get().strip()
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        price = self.price_entry.get().strip()

        if not all([name, country, city, start_date, end_date, price]):
            messagebox.showwarning("Ошибка", "Все поля должны быть заполнены!")
            return None

        try:
            price = float(price)
        except ValueError:
            messagebox.showwarning("Ошибка", "Цена должна быть числом!")
            return None

        return {
            "name": name,
            "country": country,
            "city": city,
            "start_date": start_date,
            "end_date": end_date,
            "price": price
        }

    def edit_selected_tour(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите тур для редактирования!")
            return

        try:
            self.current_edit_index = self.tree.index(selected_item)
            tour = self.tours[self.current_edit_index]

            self.clear_fields()
            self.name_entry.insert(0, tour["name"])
            self.country_entry.insert(0, tour["country"])
            self.city_entry.insert(0, tour["city"])
            self.start_date_entry.insert(0, tour["start_date"])
            self.end_date_entry.insert(0, tour["end_date"])
            self.price_entry.insert(0, str(tour["price"]))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить тур: {str(e)}")
            self.current_edit_index = None

    def delete_tour(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите тур для удаления!")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранный тур?"):
            index = self.tree.index(selected_item)
            del self.tours[index]
            self.save_data()
            self.update_tree()
            if self.current_edit_index == index:
                self.current_edit_index = None
                self.clear_fields()

    def clear_fields(self):
        for entry in [self.name_entry, self.country_entry, self.city_entry,
                      self.start_date_entry, self.end_date_entry, self.price_entry]:
            entry.delete(0, tk.END)
        self.current_edit_index = None

    def update_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for tour in self.tours:
            self.tree.insert("", tk.END, values=(
                tour["name"],
                tour["country"],
                tour["city"],
                tour["start_date"],
                tour["end_date"],
                tour["price"]
            ))

    def on_closing(self):
        self.save_data()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TourManagerApp(root)
    root.mainloop()
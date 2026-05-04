import json
import os
from tkinter import *
from tkinter import ttk, messagebox
from pathlib import Path

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.root.geometry("850x550")

        # Определяем путь к файлу данных в папке пользователя
        self.data_file = Path.home() / "book_tracker_data.json"
        
        # Данные
        self.books = []
        self.current_filtered_books = []  # Для отслеживания отфильтрованных книг
        self.load_data()

        # Виджеты ввода
        input_frame = LabelFrame(root, text="Добавить книгу", padx=10, pady=10)
        input_frame.pack(pady=10, padx=10, fill="x")

        Label(input_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.title_entry = Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        Label(input_frame, text="Автор:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.author_entry = Entry(input_frame, width=30)
        self.author_entry.grid(row=0, column=3, padx=5, pady=5)

        Label(input_frame, text="Жанр:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.genre_entry = Entry(input_frame, width=30)
        self.genre_entry.grid(row=1, column=1, padx=5, pady=5)

        Label(input_frame, text="Страниц:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.pages_entry = Entry(input_frame, width=30)
        self.pages_entry.grid(row=1, column=3, padx=5, pady=5)

        Button(input_frame, text="Добавить книгу", command=self.add_book, bg="green", fg="white").grid(row=2, column=0, columnspan=4, pady=10)

        # Фильтры
        filter_frame = LabelFrame(root, text="Фильтры", padx=10, pady=10)
        filter_frame.pack(pady=10, padx=10, fill="x")

        Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, padx=5, pady=5)
        self.genre_filter_entry = Entry(filter_frame, width=20)
        self.genre_filter_entry.grid(row=0, column=1, padx=5, pady=5)

        Label(filter_frame, text="Страниц больше:").grid(row=0, column=2, padx=5, pady=5)
        self.pages_filter_entry = Entry(filter_frame, width=10)
        self.pages_filter_entry.grid(row=0, column=3, padx=5, pady=5)

        Button(filter_frame, text="Применить фильтр", command=self.filter_books, bg="blue", fg="white").grid(row=0, column=4, padx=5, pady=5)
        Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter, bg="orange", fg="white").grid(row=0, column=5, padx=5, pady=5)

        # Кнопки управления (удаление)
        control_frame = Frame(root)
        control_frame.pack(pady=5)

        Button(control_frame, text="🗑 Удалить выбранную книгу", command=self.delete_selected_book, bg="red", fg="white", font=("Arial", 10, "bold")).pack(side=LEFT, padx=5)
        Button(control_frame, text="📊 Статистика", command=self.show_statistics, bg="purple", fg="white", font=("Arial", 10, "bold")).pack(side=LEFT, padx=5)

        # Таблица
        columns = ("Название", "Автор", "Жанр", "Страниц")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", selectmode="browse")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(root, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.pack(pady=10, padx=10, fill="both", expand=True)

        # Привязываем двойной щелчок для просмотра информации
        self.tree.bind("<Double-1>", self.show_book_info)

        self.display_books(self.books)

    def add_book(self):
        try:
            title = self.title_entry.get().strip()
            author = self.author_entry.get().strip()
            genre = self.genre_entry.get().strip()
            pages = self.pages_entry.get().strip()

            if not title or not author or not genre or not pages:
                messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                return
            
            if not pages.isdigit():
                messagebox.showerror("Ошибка", "Количество страниц должно быть числом!")
                return

            pages = int(pages)
            if pages <= 0:
                messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
                return

            # Проверка на дубликат
            for book in self.books:
                if book["title"].lower() == title.lower() and book["author"].lower() == author.lower():
                    messagebox.showerror("Ошибка", "Такая книга уже существует!")
                    return

            self.books.append({
                "title": title,
                "author": author,
                "genre": genre,
                "pages": pages
            })
            
            self.save_data()
            self.display_books(self.books)
            self.clear_entries()
            messagebox.showinfo("Успех", f"Книга '{title}' добавлена!")
            
        except PermissionError:
            messagebox.showerror("Ошибка", "Нет прав для записи в файл. Попробуйте запустить программу от имени администратора.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def delete_selected_book(self):
        """Удаление выбранной книги"""
        selected_item = self.tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите книгу для удаления!")
            return
        
        # Получаем данные выбранной книги
        values = self.tree.item(selected_item)["values"]
        if not values:
            return
        
        title, author, genre, pages = values
        
        # Подтверждение удаления
        result = messagebox.askyesno(
            "Подтверждение удаления", 
            f"Вы уверены, что хотите удалить книгу:\n\n"
            f"Название: {title}\n"
            f"Автор: {author}\n"
            f"Жанр: {genre}\n"
            f"Страниц: {pages}\n\n"
            f"Это действие нельзя отменить!"
        )
        
        if result:
            # Удаляем книгу из списка
            for i, book in enumerate(self.books):
                if (book["title"] == title and 
                    book["author"] == author and 
                    book["genre"] == genre and 
                    book["pages"] == int(pages)):
                    del self.books[i]
                    break
            
            # Сохраняем изменения
            self.save_data()
            
            # Обновляем отображение
            if self.genre_filter_entry.get().strip() or self.pages_filter_entry.get().strip():
                # Если активен фильтр, применяем его заново
                self.filter_books()
            else:
                self.display_books(self.books)
            
            messagebox.showinfo("Успех", f"Книга '{title}' успешно удалена!")

    def show_book_info(self, event):
        """Показывает информацию о книге при двойном щелчке"""
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item)["values"]
            if values:
                title, author, genre, pages = values
                info = f"📖 Информация о книге:\n\n"
                info += f"Название: {title}\n"
                info += f"Автор: {author}\n"
                info += f"Жанр: {genre}\n"
                info += f"Количество страниц: {pages}\n"
                
                # Дополнительная информация
                if int(pages) < 100:
                    info += f"\n📚 Короткая книга (меньше 100 страниц)"
                elif int(pages) > 500:
                    info += f"\n📖 Объёмная книга (больше 500 страниц)"
                else:
                    info += f"\n📕 Книга среднего объёма"
                
                messagebox.showinfo("Информация о книге", info)

    def show_statistics(self):
        """Показывает статистику по книгам"""
        if not self.books:
            messagebox.showinfo("Статистика", "Нет добавленных книг для статистики.")
            return
        
        total_books = len(self.books)
        total_pages = sum(book["pages"] for book in self.books)
        avg_pages = total_pages // total_books if total_books > 0 else 0
        
        # Жанры
        genres = {}
        for book in self.books:
            genre = book["genre"]
            genres[genre] = genres.get(genre, 0) + 1
        
        most_common_genre = max(genres, key=genres.get) if genres else "Нет"
        
        # Самые длинные и короткие книги
        longest_book = max(self.books, key=lambda x: x["pages"]) if self.books else None
        shortest_book = min(self.books, key=lambda x: x["pages"]) if self.books else None
        
        stats = f"📊 Статистика книг:\n\n"
        stats += f"📚 Всего книг: {total_books}\n"
        stats += f"📄 Всего страниц: {total_pages}\n"
        stats += f"📈 Среднее кол-во страниц: {avg_pages}\n"
        stats += f"🎭 Самый популярный жанр: {most_common_genre} ({genres.get(most_common_genre, 0)} книг)\n\n"
        
        if longest_book:
            stats += f"🏆 Самая длинная книга:\n   • {longest_book['title']} - {longest_book['pages']} стр.\n\n"
        if shortest_book:
            stats += f"📖 Самая короткая книга:\n   • {shortest_book['title']} - {shortest_book['pages']} стр.\n\n"
        
        stats += f"🎨 Жанры:\n"
        for genre, count in sorted(genres.items(), key=lambda x: x[1], reverse=True):
            stats += f"   • {genre}: {count} книг\n"
        
        messagebox.showinfo("Статистика книг", stats)

    def display_books(self, books):
        self.current_filtered_books = books
        for row in self.tree.get_children():
            self.tree.delete(row)
        for book in books:
            self.tree.insert("", END, values=(book["title"], book["author"], book["genre"], book["pages"]))

    def filter_books(self):
        try:
            genre_filter = self.genre_filter_entry.get().strip().lower()
            pages_filter = self.pages_filter_entry.get().strip()

            filtered = self.books[:]
            
            if genre_filter:
                filtered = [b for b in filtered if genre_filter in b["genre"].lower()]
            
            if pages_filter:
                if pages_filter.isdigit():
                    filtered = [b for b in filtered if b["pages"] > int(pages_filter)]
                else:
                    messagebox.showerror("Ошибка", "Фильтр по страницам должен быть числом!")
                    return

            self.display_books(filtered)
            
            if len(filtered) == 0:
                messagebox.showinfo("Результат", "Книги по заданным фильтрам не найдены.")
            else:
                messagebox.showinfo("Результат", f"Найдено книг: {len(filtered)}")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при фильтрации: {str(e)}")

    def reset_filter(self):
        """Сброс фильтров"""
        self.genre_filter_entry.delete(0, END)
        self.pages_filter_entry.delete(0, END)
        self.display_books(self.books)

    def clear_entries(self):
        self.title_entry.delete(0, END)
        self.author_entry.delete(0, END)
        self.genre_entry.delete(0, END)
        self.pages_entry.delete(0, END)

    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.books, f, indent=4, ensure_ascii=False)
            print(f"Данные сохранены в: {self.data_file}")  # Для отладки
        except PermissionError:
            raise PermissionError(f"Нет прав для записи в {self.data_file}")
        except Exception as e:
            raise Exception(f"Ошибка при сохранении: {str(e)}")

    def load_data(self):
        """Загрузка данных из JSON файла"""
        try:
            if self.data_file.exists():
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.books = json.load(f)
                print(f"Данные загружены из: {self.data_file}")
            else:
                self.books = []
                print("Создан новый файл данных")
        except Exception as e:
            print(f"Ошибка при загрузке: {str(e)}")
            self.books = []

if __name__ == "__main__":
    try:
        root = Tk()
        app = BookTracker(root)
        root.mainloop()
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        messagebox.showerror("Критическая ошибка", f"Не удалось запустить программу: {str(e)}")
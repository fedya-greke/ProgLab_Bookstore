import os
from models import BookStore, Order
from file_handlers import FileHandler
from exceptions import NotEnoughMoney

class DigitalBookStoreApp:
    def __init__(self):
        """Инициализация приложения, указание путей к файлам"""
        self.BookStore = BookStore()
        self.data_dir = "data" # Папка для хранения файлов данных
        self.json_file = os.path.join(self.data_dir, "books.json")
        self.xml_file = os.path.join(self.data_dir, "books.xml")

        os.makedirs(self.data_dir, exist_ok=True)

        self.load_data()

    def load_data(self) -> None:
        """Пытается загрузить данные при запуке приложения
        Сначала проверяет наличие JSON файла, потом XML
        Если файлов нет - создает новый пустой магазин"""
        try:
            if os.path.exists(self.json_file):
                # Загружаем из JSON
                self.bookstore = FileHandler.load_from_json_file(self.json_file)
                print("Данные загружены из json файла")
            elif os.path.exists(self.xml_file):
                # Загружаем из XML файла
                self.bookstore = FileHandler.load_from_xml_file(self.xml_file)
                print("Данные заугуженны из xml файла")
            else:
                # Файлы не найдены
                print("Файлы не найдены, создаём новый магазин")
        except Exception as e:
            # Обрабатываем любые ошибки при загрузке
            print(f"Ошибка при загрузке данных: {e}")
            print("Продолжаем с пустым магазином")

    def save_data(self) -> None:
        """Сохраняет данные в нужные файлы. Вызов при выходе из магазина"""
        try:
            FileHandler.save_to_json_file(self.bookstore, self.json_file)
            FileHandler.save_to_xml_file(self.bookstore, self.xml_file)
            print("Данные сохранены")
        except Exception as e:
            # Обрабатываем любые ошибки при сохранении
            print(f"Ошибка при сохранении данных: {e}")

    def display_menu(self) -> None:
        """Главное меню с возможными опциями"""
        print("\n" + "=" * 50)
        print("МАГАЗИН ЦИФРОВЫХ КНИГ - ГЛАВНОЕ МЕНЮ")
        print("=" * 50)
        print("1. Управление книгами")
        print("2. Управление покупателями")
        print("3. Управление заказами")
        print("4. Поиск и просмотр")
        print("5. Сохранить данные")
        print("6. Загрузить данные")
        print("0. Выход")
        print("=" * 50)

    def books_menu(self) -> None:
        """Для книг (1)"""
        while True:
            print("\n" + "=" * 30)
            print("УПРАВЛЕНИЕ КНИГАМИ")
            print("=" * 30)
            print("1. Добавить книгу")
            print("2. Показать все книги")
            print("3. Найти книгу по ID")
            print("4. Найти книгу по названию")
            print("5. Удалить книгу")
            print("0. Назад в главное меню")

            choice = input("Выберите действие: ").strip()

            if choice == "1":
                self.add_book()
            elif choice == "2":
                self.show_all_books()
            elif choice == "3":
                self.find_book_by_id()
            elif choice == "4":
                self.find_book_by_title()
            elif choice == "5":
                self.delete_book()
            elif choice == "0":
                break
            else:
                print("Неверный выбор. Попробуйте снова.")

    def add_book(self) -> None:
        """Добавляет новую книгу в магазин"""
        try:
            print("\nДОБАВЛЕНИЕ НОВОЙ КНИГИ")

            # Создать или выбрать автора
            if not self.bookstore.authors:
                print("Сначала нужно добавить автора")
                self.add_author()
                # После добавления автора
                if not self.bookstore.authors:
                    print("Не удалось добавить автора")
                    return
                author = self.bookstore.authors[-1]  # Берем последнего добавленного автора
            else:
                # Показываем существующих авторов для выбора
                print("\nСуществующие авторы:")
                for i, author in enumerate(self.bookstore.authors, 1):
                    print(f"{i}. {author.name} ({author.country})")

                choice = input("\nВыберите автора (номер) или введите 'new' для нового автора: ")
                if choice.lower() == 'new':
                    self.add_author()
                    if not self.bookstore.authors:
                        return
                    author = self.bookstore.authors[-1]
                else:
                    try:
                        index = int(choice) - 1
                        author = self.bookstore.authors[index]
                    except (ValueError, IndexError):
                        print("Неверный выбор. Создаем нового автора.")
                        self.add_author()
                        if not self.bookstore.authors:
                            return
                        author = self.bookstore.authors[-1]

            # Ввод данных книги
            title = input("Название книги: ").strip()
            if not title:
                print("Название не может быть пустым")
                return

            price = float(input("Цена книги: ").strip())
            genre = input("Жанр книги: ").strip() or "Не указан"

            # Создаем и добавляем книгу в магазин
            book = self.bookstore.add_book(title, author, price, genre)
            print(f"Книга '{book.title}' успешно добавлена! ID: {book.book_id}")

        except NotEnoughMoney as e:
            print(f"Ошибка цены: {e}")
        except ValueError as e:
            print(f"Ошибка ввода: {e}")
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")

    def add_author(self) -> None:
        """Добавляем нового автора"""
        try:
            print("Добавление нового автора")
            name = input("Введите имя автора: ").strip()
            if not name:
                print("Имя автора не может быть пустым")
                return None

            country = input("Введите страну автора").strip() or "Страна не известна"

            # Создаём и добавляем автора
            author = self.bookstore.add_author(name, country)
            print(f"Автор '{author.name}' успешно добавлен! ID: {author.author_id}")

        except Exception as e:
            print(f"Ошибка при добавлении автора: {e}")
            return None

    def show_all_books(self) -> None:
        """Список всех книг в магазине и основная информация по ним"""
        if not self.bookstore.books:
            print("В магазине пока нет книг")
            return
        print(f"\nВСЕ КНИГИ ({len(self.bookstore.books)} шт.):")
        for book in self.bookstore.books:
            print(f"  ID: {book.book_id} | '{book.title}' | {book.author.name} "
                  f"| {book.price} руб. | {book.genre}")

    def find_book_by_id(self) -> None:
        """Находим книгу по её айди"""
        title = input("Введите название книги (или часть): ").strip().lower()
        if not title:
            print("Введите название для поиска")
            return
        # Ищем книги, содержащие введенную подстроку в названии
        found_books = [book for book in self.bookstore.books if title in book.title.lower()]
        if not found_books:
            print("Книги не найдены")
            return
        print(f"\nНАЙДЕНО КНИГ: {len(found_books)}")
        for book in found_books:
            print(f"  ID: {book.book_id} | '{book.title}' | {book.author.name} | {book.price} руб.")

    def delete_book(self) -> None:
        """Удаляет книгу по ID"""
        try:
            self.show_all_books()
            if not self.bookstore.books:
                return

            book_id = int(input("\nВведите ID книги для удаления: ").strip())

            # Ищем книгу для удаления
            book_to_delete = None
            for book in self.bookstore.books:
                if book.book_id == book_id:
                    book_to_delete = book
                    break

            if not book_to_delete:
                print("Книга с таким ID не найдена")
                return

            # Проверяем, используется ли книга в заказах
            used_in_orders = False
            for order in self.bookstore.orders:
                if book_to_delete in order.books:
                    used_in_orders = True
                    break

            if used_in_orders:
                print("Нельзя удалить книгу, которая используется в заказах")
                return

            # Подтверждение удаления
            confirm = input(f"Вы уверены, что хотите удалить книгу '{book_to_delete.title}'? (y/n): ")
            if confirm.lower() == 'y':
                self.bookstore.books.remove(book_to_delete)
                print("Книга удалена")
            else:
                print("Удаление отменено")

        except ValueError:
            print("Неверный формат ID")
        except Exception as e:
            print(f"Ошибка при удалении: {e}")

    def customers_menu(self) -> None:
        """Управление покупателями (2)"""
        while True:
            print("\n" + "=" * 30)
            print("УПРАВЛЕНИЕ ПОКУПАТЕЛЯМИ")
            print("=" * 30)
            print("1. Добавить покупателя")
            print("2. Показать всех покупателей")
            print("3. Пополнить баланс")
            print("4. Показать покупки покупателя")
            print("0. Назад в главное меню")

            choice = input("Выберете действие: ").strip()

            if choice == "1":
                self.add_customer()
            elif choice == "2":
                self.show_all_customers()
            elif choice == "3":
                self.add_customer_funds()
            elif choice == "4":
                self.show_customer_purchases()
            elif choice == "0":
                break
            else:
                print("Неверный выбор. Попробуйте снова.")

    def add_customer(self) -> None:
        """Добавляем нового покупателя"""
        try:
            print("Добавление нового покупателя")
            name = input("Введите имя покупателя: ").strip()
            if not name:
                print("Имя не может быть пустым")
                return

            email = input("Email: ").strip()
            balance = float(input("Начальный баланс: ").strip() or "0")
            customer = self.bookstore.add_customer(name, email, balance)
            print(f"Покупатель '{customer.name}' успешно добавлен! ID: {customer.customer_id}")\

        except ValueError:
            print("Неверный формат баланса")
        except Exception as e:
            print(f"Ошибка: {e}")

    def show_all_customers(self) -> None:
        """Отображает список всех покупателей магазина"""
        if not self.bookstore.customers:
            print("В магазине пока нет покупателей")
            return

        print(f"\nВСЕ ПОКУПАТЕЛИ ({len(self.bookstore.customers)} шт.):")
        for customer in self.bookstore.customers:
            print(f"  ID: {customer.customer_id} | {customer.name} | {customer.email} |"
                f" Баланс: {customer.balance} руб.")

    def add_customer_funds(self) -> None:
        """Пополняет баланс выбранного покупателя"""
        try:
            self.show_all_customers()
            if not self.bookstore.customers:
                return

            customer_id = int(input("\nВведите ID покупателя: ").strip())
            amount = float(input("Сумма пополнения: ").strip())

            # Находим покупателя и пополняем баланс
            customer = None
            for cust in self.bookstore.customers:
                if cust.customer_id == customer_id:
                    customer = cust
                    break

            if not customer:
                print("Покупатель не найден")
                return

            customer.balance += amount  # Просто увеличиваем баланс
            print(f"Баланс пополнен. Новый баланс: {customer.balance} руб.")

        except ValueError:
            print("Неверный формат данных")
        except Exception as e:
            print(f"{e}")
    def show_customer_purchases(self) -> None:
        try:
            self.show_all_customers()
            if not self.bookstore.customers:
                return

            customer_id = int(input("\nВведите ID покупателя: ").strip())
            customer = self.bookstore.find_customer(customer_id)

            print(f"\nПОКУПКИ {customer.name}:")
            if not customer.purchased_books:
                print("Пока нет покупок")
                return
            for i, book in enumerate(customer.purchased_books, 1):
                print(f"  {i}. '{book.title}' - {book.author.name} ({book.price} руб.)")
        except Exception as e:
            print(f"{e}")
    def orders_menu(self) -> None:
        """Подменю для управления заказами (3)"""
        while True:
            print("\n" + "=" * 30)
            print("УПРАВЛЕНИЕ ЗАКАЗАМИ")
            print("=" * 30)
            print("1. Создать заказ")
            print("2. Показать все заказы")
            print("3. Обработать заказ")
            print("4. Отменить заказ")
            print("0. Назад в главное меню")

            choice = input("Выберите действие: ").strip()

            if choice == "1":
                self.create_order()
            elif choice == "2":
                self.show_all_orders()
            elif choice == "3":
                self.process_order()
            elif choice == "4":
                self.cancel_order()
            elif choice == "0":
                break
            else:
                print("Неверный выбор. Попробуйте снова.")
    def create_order(self) -> None:
        """Создаём новый заказ для покупателя"""
        try:
            print("Создание нового заказа")
            self.show_all_customers()
            if not self.bookstore.customers:
                print("Нет покупателей для заказа")
                return

            customer_id = int(input("Введите айди покупателя").strip())
            customer = None
            for cust in self.bookstore.customers:
                if cust.customer_id == customer_id:
                    customer = cust
                    break
            if not customer:
                print("Покупатель не найден")
                return

            # Выбираем книги в заказ
            self.show_all_books()
            if not self.bookstore.customers:
                print("Нет книги для заказа")
                return

            book_ids_input = input("Введите айди книг через запятую: ").strip()
            book_ids = [int(id_str.strip()) for id_str in book_ids_input.split(",")]
            # Находим книги по ID
            books = []
            for book_id in book_ids:
                for book in self.bookstore.books:
                    if book.book_id == book_id:
                        books.append(book)
                        break
            if not books:
                print("Не найдено книг с указанными ID")
                return
            # Создание заказа
            order_id = self.bookstore._next_order_id
            order = Order(self.bookstore._next_order_id, customer, books)
            self.bookstore.orders.append(order)
            self.bookstore._next_order_id += 1

            print(f"Заказ создан, ID: {order.order_id}")
            print(f"Общая стоимость: {order.total_price} руб.")
            print(f"Баланс покупателя: {customer.balance} руб.")

            """
            # Предлагаем обработать заказ сейчас и списываем деньги
            process_now = input("Обработать заказ сейчас? (y/n): ").strip().lower()
            if process_now == 'y':
                success = order.process_order()
                if order.process_order():
                    print("Заказ успешно обработан!")
                    print(f"Новый баланс: {customer.balance} руб.")
                else:
                    print("Не удалось обработать заказ")
            else:
                print("Заказ создан, но не обработан")
            """
        except ValueError as e:
            print(f"Ошибка ввода данных{e}")
        except Exception as e:
            print(f"Ошибка при создании заказа: {e}")

    def show_all_orders(self) -> None:
        """Отображение списка всех заказов"""
        if not self.bookstore.customers:
            print("Заказов пока нет")
            return
        print(f"Все заказы {len(self.bookstore.customers)} шт.")
        for order in self.bookstore.orders:
            print(f" ID: {order.order_id} | {order.customer.name} | {order.total_price} руб."
                  f"| {order.status}")

    def process_order(self) -> None:
        """Обрабатывает заказ"""
        try:
            self.show_all_orders()
            if not self.bookstore.orders:
                return

            order_id = int(input("\nВведите ID заказа для обработки: ").strip())

            # Находим заказ
            order_to_process = None
            for order in self.bookstore.orders:
                if order.order_id == order_id:
                    order_to_process = order
                    break

            if not order_to_process:
                print("Заказ с таким ID не найден")
                return

            print(f"Обрабатываем заказ #{order_id}")
            print(f"Текущий статус: {order_to_process.status}")
            print(f"Баланс покупателя: {order_to_process.customer.balance}")
            print(f"Сумма заказа: {order_to_process.total_price}")

            # Пытаемся обработать заказ
            if order_to_process.process_order():
                print("Заказ успешно обработан!")
                print(f"Новый баланс покупателя: {order_to_process.customer.balance}")
            else:
                print("Не удалось обработать заказ")
                print("Возможные причины:")
                print("- Заказ уже обработан")
                print("- Недостаточно средств")
                print("- Ошибка в статусе заказа")

        except ValueError:
            print("Неверный формат ID")
        except Exception as e:
            print(f"Ошибка: {e}")

    def cancel_order(self) -> None:
        """Отменяет заказ и возвращает деньги покупателю"""
        try:
            self.show_all_orders()
            if not self.bookstore.orders:
                return

            order_id = int(input("\nВведите ID заказа для отмены: ").strip())
            order = None
            for ord in self.bookstore.orders:
                if ord.order_id == order_id:
                    order = ord
                    break

            if not order:
                print("Заказ с таким ID не найден")
                return

            confirm = input(f"Вы уверены, что хотите отменить заказ #{order_id}? (y/n): ")
            if confirm.lower() == 'y':
                if order.cancel_order():
                    print("Заказ отменен")
                else:
                    print("Не удалось отменить заказ")
            else:
                print("Отмена отменена")

        except ValueError:
            print("Неверный формат ID")
        except Exception as e:
            print(f"Ошибка: {e}")
    def search_menu(self) -> None:
        """Для поиска и просмотра статистики (4)"""
        while True:
            print("\n" + "=" * 30)
            print("ПОИСК И ПРОСМОТР")
            print("=" * 30)
            print("1. Показать статистику магазина")
            print("2. Найти книги по автору")
            print("3. Показать все заказы покупателя")
            print("0. Назад в главное меню")

            choice = input("Выберите действие: ").strip()

            if choice == "1":
                self.show_store_stats()
            elif choice == "2":
                self.find_books_by_author()
            elif choice == "3":
                self.show_customer_orders()
            elif choice == "0":
                break
            else:
                print("Неверный выбор. Попробуйте снова.")
    def show_store_stats(self) -> None:
        """Показать статус магазина"""
        print("\nСТАТИСТИКА МАГАЗИНА:")
        print(f"  Книг: {len(self.bookstore.books)}")
        print(f"  Авторов: {len(self.bookstore.authors)}")
        print(f"  Покупателей: {len(self.bookstore.customers)}")
        print(f"  Заказов: {len(self.bookstore.orders)}")

        # Выручка по завершённым заказам
        if self.bookstore.orders:
            total_revenue = sum(order.total_price for order in self.bookstore.orders
                                if order.status == "completed")
            print(f"  Общая выручка: {total_revenue} руб.")
    def find_books_by_author(self) -> None:
        """Находит все книги автора"""
        if not self.bookstore.authors:
            print("Авторов пока нет")
            return

        print("\nВЫБЕРЕТЕ АВТОРА:")
        for i, author in enumerate(self.bookstore.authors, 1):
            print(f"{i}. '{author.name}' - {author.country}")
        try:
            choice = int(input("Введите номер автора:").strip()) - 1
            author = self.bookstore.authors[choice]

            # Поиск книг данного автора
            author_books = [book for book in self.bookstore.books if book.author.author_id == author.author_id]
            if not author_books:
                print(f"У автора '{author.name}' пока нет книг в магазине")
                return

            print(f"\nКнига автора {author.name}")
            for book in author_books:
                print(f"  - '{book.title}' | {book.price} руб. | {book.genre}")

        except (ValueError, IndexError):
            print("Неверный выбор")

    def find_book_by_title(self) -> None:
        """Находит книги по частичному совпадению названия"""
        title = input("Введите название книги (или часть): ").strip().lower()
        if not title:
            print("Введите название для поиска")
            return

        # Ищем книги по названию
        found_books = []
        for book in self.bookstore.books:
            if title in book.title.lower():
                found_books.append(book)

        if not found_books:
            print("Книги не найдены")
            return

        print(f"\nНАЙДЕНО КНИГ: {len(found_books)}")
        for book in found_books:
            print(f"  ID: {book.book_id} | '{book.title}' | {book.author.name} | {book.price} руб.")

    def show_customer_orders(self) -> None:
        """Все заказы выбранного покупателя"""
        try:
            self.show_all_customers()
            if not self.bookstore.customers:
                print("Покупателей пока нет")
                return

            customer_id = int(input("\nВведите ID покупателя: ").strip())
            customer = self.bookstore.find_customer(customer_id)
            orders = self.bookstore.get_customer_orders(customer_id)

            if not orders:
                print(f"У покупателя '{customer.name}' пока нет заказов")
                return

            print(f"\nЗАКАЗЫ ПОКУПАТЕЛЯ '{customer.name}':")
            for order in orders:
                print(f"\n  Заказ #{order.order_id}:")
                print(f"    Дата: {order.order_date}")
                print(f"    Статус: {order.status}")
                print(f"    Сумма: {order.total_price} руб.")
                print(f"    Книги: {len(order.books)} шт.")
        except Exception as e:
            print(f"{e}")

    def run(self) -> None:
        """Главный цикл приложения, пользовательский ввод, управление навигацией по меню"""
        print("Добро пожаловать в Магазин Цифровых Книг!")

        while True:
            try:
                self.display_menu()
                choice = input("Выберите действие: ").strip()

                # Обработка выбора в главном меню
                if choice == "1":
                    self.books_menu()
                elif choice == "2":
                    self.customers_menu()
                elif choice == "3":
                    self.orders_menu()
                elif choice == "4":
                    self.search_menu()
                elif choice == "5":
                    self.save_data()
                elif choice == "6":
                    self.load_data()
                elif choice == "0":
                    self.save_data()  # Сохраняем данные при выходе (0)
                    print("До свидания! Данные сохранены.")
                    break
                else:
                    print("Неверный выбор. Попробуйте снова.")

            except KeyboardInterrupt:
                # Обрабатываем прерывание программы (Alt + F4)
                print("\nПрограмма прервана пользователем")
                self.save_data()
                break
            except Exception as e:
                # Обрабатываем все непредвиденные ошибки
                print(f"Неожиданная ошибка: {e}")

        # Точка входа в программу
if __name__ == "__main__":
    # Создаем экземпляр приложения и запускаем его
    app = DigitalBookStoreApp()
    app.run()




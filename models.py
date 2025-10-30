from exceptions import InvalidPrice
"""Классы:
BookStore - магазин
Book - цифровая книга
Author - автор книги
Customer - покупатель
Order - заказ"""

class Author:
    """Автор книги и его данные"""
    def __init__(self, author_id: int, author_name: str, country: str = "Неизвестно", birthday: str = "Неизвестно") -> None:
        self.author_id = author_id
        self.author_name = author_name
        self.country = country
        self.birthday = birthday
    def get_info(self) -> str:
        return f"Автор: {self.author_name}, Страна: {self.country}, Дата рождения: {self.birthday}"
    def __str__(self) -> str:
        """Метод класса, вызывается когда преобразуем объект в строку"""
        return f"{self.author_name}"

class Book:
    """Цифровая книга"""
    def __init__(self, book_id: int,  book_title: str, author_name: Author, book_price: float,
                 genre: str = "Не указан", rating: float = 0.0) -> None:
        self.book_id = book_id
        self.book_title = book_title
        self.author_name = author_name
        self.book_price = book_price
        self.genre = genre
        self.rating = rating
        # Проверка цены
        if self.book_price <= 0:
            raise InvalidPrice(book_price)
    def get_info(self) -> str:
        """Подробная информация о книге"""
        return (f"Книга: {self.book_title}\n"
                f"Автор: {self.author_name}\n"
                f"Цена: {self.book_price}\n"
                f"Жанр: {self.genre}\n"
                f"Рейтинг: {self.rating}")
    def apply_discount(self, discount_persent: float) -> None:
        """Применяет скидку к покупке"""
        if 0 < discount_persent <= 100:
            self.book_price = self.book_price * ( 1 - discount_persent / 100)
    def __str__(self) -> str:
        return f"{self.book_title}"

class Customer:
    """Класс покупатель"""
    def __init__(self, customer_id: int,name: str, email: str, balance: float) -> None:
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.balance = balance
        self.purchased_book: list[Book] = [] #Купленные книги
    def add_money(self, amount: float) -> None:
        """Пополнение боланса"""
        if amount <= 0:
            self.balance += amount
    def can_afford(self, amount: float) -> bool:
        """Хватает ли денег"""
        return self.balance >= amount
    def purchase_book(self, book: Book) -> bool:
        """Покупка книги"""
        if self.can_afford(book.book_price):
            self.balance -= book.book_price
            self.purchased_book.append(book)
            return True
        return False
    def get_info(self) -> str:
        return f"Покупатель: {self.name}, Почта: {self.email}, Баланс: {self.balance} руб."
    def __str__(self) -> str:
        return f"{self.name}"
class Order:
    """Класс заказ"""
    def __init__(self, order_id: int, customer: Customer, books: list[Book]) -> None:
        self.order_id = order_id
        self.customer = customer
        self.books = books.copy()
        self.status = "Created"
        self.order_date = self.get_date()
        self.total_price = self.calculate_total()
    def get_date(self) -> str:
        """Текущая дата"""
        from datetime import datetime
        return datetime.now().strftime("%Y/%m/%d %H:%M")
    def calculate_total(self) -> float:
        """Общая стоимость"""
        return sum(book.book_price for book in self.books)

    def process_order(self) -> bool:
        """Обрабатывает заказ - списывает деньги и выдает книги"""
        if self.status != "created":
            return False

        total = self.calculate_total()

        # Проверяем достаточно ли денег
        if not self.customer.can_afford(total):
            return False

        # Списываем деньги
        self.customer.balance -= total

        # Добавляем книги в список покупок
        self.customer.purchased_book.extend(self.books)

        self.status = "completed"
        return True

    def cancel_order(self) -> bool:
        """Отменяет заказ и возвращает деньги"""
        if self.status == "completed":
            # Возвращаем деньги
            self.customer.balance += self.total_price
            # Убираем книги из списка покупок
            for book in self.books:
                if book in self.customer.purchased_book:
                    self.customer.purchased_book.remove(book)

        self.status = "cancelled"
        return True
    def get_order_info(self) -> str:
        """Возвращает информацию о заказе"""
        books_info = "\n".join(f"  - {book.book_title} ({book.book_price} руб.)" for book in self.books)
        return (f"Заказ #{self.order_id}\n"
                f"Покупатель: {self.customer.name}\n"
                f"Дата: {self.order_date}\n"
                f"Статус: {self.status}\n"
                f"Общая стоимость: {self.total_price} руб.\n"
                f"Книги:\n{books_info}")

    def __str__(self) -> str:
        return f"Заказ #{self.order_id} - {self.customer.name} - {self.total_price} руб. - {self.status}"

class BookStore:
    """Основной класс, управляет над другими"""
    def __init__(self):
        self.books: list[Book] = []
        self.authors: list[Author] = []
        self.customers: list[Customer] = []
        self.orders: list[Order] = []

        # Счетчики для ID
        self._next_book_id = 1
        self._next_author_id = 1
        self._next_customer_id = 1
        self._next_order_id = 1

    # CRUD операции для Customer
    def add_customer(self, name: str, email: str, balance: float = 0.0) -> Customer:
        """Добавляет нового покупателя"""
        customer = Customer(self._next_customer_id, name, email, balance)
        self._next_customer_id += 1
        self.customers.append(customer)
        return customer

    def find_customer(self, customer_id: int) -> Customer:
        """Находит покупателя по ID"""
        for customer in self.customers:
            if customer.customer_id == customer_id:
                return customer
        raise ValueError(f"Покупатель с ID {customer_id} не найден")

    def get_all_customers(self) -> list[Customer]:
        """Возвращает всех покупателей"""
        return self.customers.copy()

    def create_order(self, customer_id: int, book_ids: list[int]) -> Order:
        """Создает новый заказ"""
        try:
            customer = self.find_customer(customer_id)
            books = [self.find_book(book_id) for book_id in book_ids]

            order = Order(self._next_order_id, customer, books)
            self._next_order_id += 1
            self.orders.append(order)

            return order
        except ValueError as error:
            raise ValueError(f"Ошибка создания заказа: {error}")

    def add_author(self, name: str, country: str = "Неизвестно") -> Author:
        """Добавляет нового автора"""
        author = Author(self._next_author_id, name, country)
        self._next_author_id += 1
        self.authors.append(author)
        return author

    def add_book(self, title: str, author: Author, price: float,
                 genre: str = "Не указан") -> Book:
        """Добавляет новую книгу"""
        book = Book(self._next_book_id, title, author, price, genre)
        self._next_book_id += 1
        self.books.append(book)
        return book

    def find_book(self, book_id: int) -> Book:
        """Находит книгу по ID"""
        for book in self.books:
            if book.book_id == book_id:
                return book
        raise ValueError(f"Книга с ID {book_id} не найден")

    def process_order(self, order_id: int) -> bool:
        """Обрабатывает заказ"""
        order = self.find_order(order_id)
        return order.process_order()

    def find_order(self, order_id: int) -> Order:
        """Находит заказ по ID"""
        for order in self.orders:
            if order.order_id == order_id:
                return order
        raise ValueError(f"Заказ с ID {order_id} не найден")

    def get_customer_orders(self, customer_id: int) -> list[Order]:
        """Возвращает все заказы покупателя"""
        return [order for order in self.orders if order.customer.customer_id == customer_id]

"""Тестировка"""
if __name__ == "__main__":

    """Класс Author"""

    print("Тестируем класс Author")

    # Создаем автора
    author1 = Author(1, "Лев Толстой", "Россия", "1828-09-09")

    print("1. Атрибуты объекта:")
    print("   Имя автора:", author1.author_name)
    print("   Страна:", author1.country)
    print("   Дата рождения:", author1.birthday)

    print("\n2. Вызов методов:")
    print("   author1.get_info():", author1.get_info())

    print("\n4. Автор с параметрами по умолчанию:")
    author2 = Author(1, "Джон Смит")  # только имя
    print("Автор2:", author2)

    """Класс Book"""

    print("\nТестируем класс Book")

    # Создаем автора и книгу
    author1 = Author(1, "Лев Толстой", "Россия")
    book1 = Book(1, "Война и мир", author1, 500.0, "Роман", 4.8)

    print("Книга:", book1)
    print("\nДетали:")
    print(book1.get_info())

    # Тестируем скидку
    print("\nПосле скидки 20%:")
    book1.apply_discount(20)
    print("Новая цена:", book1.book_price)

    # Тестируем исключение
    print("\nТестируем исключение")
    try:
        book_err = Book(1, "Ошибка", author1, -100.0)
    except Exception as e:
        print("Поймали ошибку:", e)
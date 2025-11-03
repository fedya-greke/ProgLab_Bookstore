import json
import xml.etree.ElementTree as ET
from models import BookStore, Book, Author, Customer, Order
class FileHandler:
    """Для работы с json и XML"""

    @staticmethod
    def save_to_json_file(bookstore: BookStore, filename: str) -> None:
        """Сохраняем в json"""
        # Главный словарь с данными
        data = {
            # Сохраняем текущие счетчики ID
            "next_ids":{
                "book": bookstore._next_book_id,
                "author": bookstore._next_author_id,
                "customer": bookstore._next_customer_id,
                "order": bookstore._next_order_id
            },
            # Список словорей авторов
            "authors": [
                {
                    "author_id": author.author_id,
                    "name": author.name,
                    "country": author.country
                }
                for author in bookstore.authors # проходим по всем элементам
            ],
            # Список словарей книг
            "books": [
                {
                    "book_id": book.book_id,
                    "title": book.title,
                    "author_id": book.author.author_id,  # сохраняем ID автора
                    "price": book.price,
                    "genre": book.genre,
                    "rating": book.rating
                }
                for book in bookstore.books
            ],
            # Спиок словарей покупателей
            "customers": [
                {
                    "customer_id": customer.customer_id,
                    "name": customer.name,
                    "email": customer.email,
                    "balance": customer.balance,
                    # Запоминаем айди купленныйх книг
                    "purchased_book_ids": [book.book_id for book in customer.purchased_books]
                }
                for customer in bookstore.customers
            ],
            # Спиок словарей заказов
            "orders": [
                {
                    "order_id": order.order_id,
                    "customer_id": order.customer.customer_id,
                    "book_ids": [book.book_id for book in order.books],
                    "order_date": order.order_date,
                    "status": order.status,
                    "total_price": order.total_price
                }
                for order in bookstore.orders
            ]
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    @staticmethod
    def load_from_json_file(filename: str) -> BookStore:
        """Загружаем данные из json"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            bookstore = BookStore()
            # Восстанавливаем счетчики ID
            bookstore._next_book_id = data["next_ids"]["book"]
            bookstore._next_author_id = data["next_ids"]["author"]
            bookstore._next_customer_id = data["next_ids"]["customer"]
            bookstore._next_order_id = data["next_ids"]["order"]

            # Сначала создаем авторов (они нужны для книг)
            authors_dict = {} #словарь для посика автора по айди
            for author_data in data["authors"]:
                author = Author(author_data["author_id"], author_data["name"], author_data["country"])
                bookstore.authors.append(author)
                authors_dict[author_data["author_id"]] = author

            # Создаем книги
            books_dict = {}
            for book_data in data["books"]:
                # Находим автора по сохраненному ID
                author = authors_dict[book_data["author_id"]]
                book = Book(book_data["book_id"], book_data["title"], author,
                            book_data["price"], book_data["genre"], book_data.get("rating", 0.0))
                bookstore.books.append(book)
                books_dict[book_data["book_id"]] = book

            # Создаем покупателей
            customers_dict = {}
            for customer_data in data["customers"]:
                customer = Customer(customer_data["customer_id"], customer_data["name"],
                                    customer_data["email"], customer_data["balance"])
                bookstore.customers.append(customer)
                customers_dict[customer_data["customer_id"]] = customer

                # Восстанавливаем купленные книги
                for book_id in customer_data["purchased_book_ids"]:
                    if book_id in books_dict:
                        customer.purchased_books.append(books_dict[book_id])

            # Создаем заказы
            for order_data in data["orders"]:
                customer = customers_dict[order_data["customer_id"]]
                books = [books_dict[book_id] for book_id in order_data["book_ids"] if book_id in books_dict]

                order = Order(order_data["order_id"], customer, books)
                order.order_date = order_data["order_date"]
                order.status = order_data["status"]
                order.total_price = order_data["total_price"]

                bookstore.orders.append(order)

            return bookstore

    @staticmethod
    def save_to_xml_file(bookstore: BookStore, filename: str) -> None:
        """Сохраняет данные магазина в XML файл"""
        root = ET.Element("bookstore") # корневой элемент

        # Сохраняем счетчики ID
        next_ids = ET.SubElement(root, "next_ids")
        ET.SubElement(next_ids, "book").text = str(bookstore._next_book_id)
        ET.SubElement(next_ids, "author").text = str(bookstore._next_author_id)
        ET.SubElement(next_ids, "customer").text = str(bookstore._next_customer_id)
        ET.SubElement(next_ids, "order").text = str(bookstore._next_order_id)

        # Сохраняем авторов
        authors_elem = ET.SubElement(root, "authors")
        for author in bookstore.authors:
            author_elem = ET.SubElement(authors_elem, "author")
            ET.SubElement(author_elem, "id").text = str(author.author_id)
            ET.SubElement(author_elem, "name").text = author.name
            ET.SubElement(author_elem, "country").text = author.country

        # Сохраняем книги
        books_elem = ET.SubElement(root, "books")
        for book in bookstore.books:
            book_elem = ET.SubElement(books_elem, "book")
            ET.SubElement(book_elem, "id").text = str(book.book_id)
            ET.SubElement(book_elem, "title").text = book.title
            ET.SubElement(book_elem, "author_id").text = str(book.author.author_id)
            ET.SubElement(book_elem, "price").text = str(book.price)
            ET.SubElement(book_elem, "genre").text = book.genre
            ET.SubElement(book_elem, "rating").text = str(book.rating)

        # Покупатели
        customers_elem = ET.SubElement(root, "customers")
        for customer in bookstore.customers:
            customer_elem = ET.SubElement(customers_elem, "customer")
            ET.SubElement(customer_elem, "id").text = str(customer.customer_id)
            ET.SubElement(customer_elem, "name").text = customer.name
            ET.SubElement(customer_elem, "email").text = customer.email
            ET.SubElement(customer_elem, "balance").text = str(customer.balance)
            # Сохраняем ID купленных книг
            purchased_books = ET.SubElement(customer_elem, "purchased_books")
            for book in customer.purchased_books:
                ET.SubElement(purchased_books, "book_id").text = str(book.book_id)

        # Заказы
        orders_elem = ET.SubElement(root, "orders")
        for order in bookstore.orders:
            order_elem = ET.SubElement(orders_elem, "order")
            ET.SubElement(order_elem, "id").text = str(order.order_id)
            ET.SubElement(order_elem, "customer_id").text = str(order.customer.customer_id)
            ET.SubElement(order_elem, "order_date").text = order.order_date
            ET.SubElement(order_elem, "status").text = order.status
            ET.SubElement(order_elem, "total_price").text = str(order.total_price)
            # Сохраняем ID книг в заказе
            books_elem = ET.SubElement(order_elem, "books")
            for book in order.books:
                ET.SubElement(books_elem, "book_id").text = str(book.book_id)

        tree = ET.ElementTree(root) # Сохраняяем дерево XML
        tree.write(filename, encoding='utf-8', xml_declaration=True) # Сохраняем в файл
    def load_from_xml_file(filename: str) -> BookStore:
        # Загружаем данные из xml
        # Парсим XML файл
        tree = ET.parse(filename)
        root = tree.getroot()

        # Создаем новый магазин
        bookstore = BookStore()

        # Словари для быстрого доступа
        authors_dict = {}
        books_dict = {}
        customers_dict = {}

        # 1. Восстанавливаем счетчики ID
        next_ids = root.find("next_ids")
        bookstore._next_book_id = int(next_ids.find("book").text)
        bookstore._next_author_id = int(next_ids.find("author").text)
        bookstore._next_customer_id = int(next_ids.find("customer").text)
        bookstore._next_order_id = int(next_ids.find("order").text)

        # 2. Восстанавливаем авторов
        authors_elem = root.find("authors")
        for author_elem in authors_elem.findall("author"):
            author_id = int(author_elem.find("id").text)
            name = author_elem.find("name").text
            country = author_elem.find("country").text

            author = Author(author_id, name, country)
            bookstore.authors.append(author)
            authors_dict[author_id] = author

        # 3. Восстанавливаем книги
        books_elem = root.find("books")
        for book_elem in books_elem.findall("book"):
            book_id = int(book_elem.find("id").text)
            title = book_elem.find("title").text
            author_id = int(book_elem.find("author_id").text)
            price = float(book_elem.find("price").text)
            genre = book_elem.find("genre").text
            rating = float(book_elem.find("rating").text)

            author = authors_dict[author_id]
            book = Book(book_id, title, author, price, genre, rating)
            bookstore.books.append(book)
            books_dict[book_id] = book

        # 4. Восстанавливаем покупателей
        customers_elem = root.find("customers")
        for customer_elem in customers_elem.findall("customer"):
            customer_id = int(customer_elem.find("id").text)
            name = customer_elem.find("name").text
            email = customer_elem.find("email").text
            balance = float(customer_elem.find("balance").text)

            customer = Customer(customer_id, name, email, balance)
            bookstore.customers.append(customer)
            customers_dict[customer_id] = customer

            # Восстанавливаем купленные книги
            purchased_books_elem = customer_elem.find("purchased_books")
            for book_id_elem in purchased_books_elem.findall("book_id"):
                book_id = int(book_id_elem.text)
                if book_id in books_dict:
                    customer.purchased_books.append(books_dict[book_id])

        # 5. Восстанавливаем заказы
        orders_elem = root.find("orders")
        for order_elem in orders_elem.findall("order"):
            order_id = int(order_elem.find("id").text)
            customer_id = int(order_elem.find("customer_id").text)
            order_date = order_elem.find("order_date").text
            status = order_elem.find("status").text
            total_price = float(order_elem.find("total_price").text)

            customer = customers_dict[customer_id]

            # Восстанавливаем книги в заказе
            books_elem = order_elem.find("books")
            books = []
            for book_id_elem in books_elem.findall("book_id"):
                book_id = int(book_id_elem.text)
                if book_id in books_dict:
                    books.append(books_dict[book_id])

            order = Order(order_id, customer, books)
            order.order_date = order_date
            order.status = status
            order.total_price = total_price

            bookstore.orders.append(order)

        return bookstore

if __name__ == "__main__":
    print("Тестируем работу с файлами")

    # Создаем тестовые данные
    store = BookStore()

    author1 = store.add_author("Лев Толстой", "Россия")
    author2 = store.add_author("Фёдор Достоевский", "Россия")
    author3 = store.add_author("Антон Чехов", "Россия")

    book1 = store.add_book("Война и мир", author1, 500.0, "Роман")
    book2 = store.add_book("Преступление и наказание", author2, 450.0, "Роман")
    book3 = store.add_book("Вишневый сад", author3, 300.0, "Пьеса")

    customer1 = store.add_customer("Иван Иванов", "ivan@mail.ru", 2000.0)
    customer2 = store.add_customer("Петр Петров", "petr@mail.ru", 1500.0)

    # Создаем и обрабатываем заказы
    order1 = store.create_order(customer1.customer_id, [1, 2])  # книги 1 и 2
    store.process_order(order1.order_id)

    order2 = store.create_order(customer2.customer_id, [3])  # книга 3
    store.process_order(order2.order_id)

    print("    Данные до сохранения:")
    print(f"   Авторов: {len(store.authors)}")
    print(f"   Книг: {len(store.books)}")
    print(f"   Покупателей: {len(store.customers)}")
    print(f"   Заказов: {len(store.orders)}")

    # Показываем детали
    print("\n Авторы:")
    for author in store.authors:
        print(f"   - {author}")

    print("\n Книги:")
    for book in store.books:
        print(f"   - {book}")

    print("\n Покупатели:")
    for customer in store.customers:
        print(f"   - {customer}")
        print(f"     Куплено книг: {len(customer.purchased_books)}")

    print("\n Заказы:")
    for order in store.orders:
        print(f"   - {order}")

    # ТЕСТ 1: Сохраняем и загружаем из JSON
    print(" ТЕСТ 1: Работа с JSON")

    # Сохраняем в JSON
    FileHandler.save_to_json_file(store, "data/books.json")
    print(" Данные сохранены в data/books.json")

    # Загружаем обратно из JSON
    store_from_json = FileHandler.load_from_json_file("data/books.json")
    print(" Данные загружены из JSON")

    # Проверяем что все восстановилось
    print("\n Данные после загрузки из JSON:")
    print(f"   Авторов: {len(store_from_json.authors)}")
    print(f"   Книг: {len(store_from_json.books)}")
    print(f"   Покупателей: {len(store_from_json.customers)}")
    print(f"   Заказов: {len(store_from_json.orders)}")

    # Проверяем связи
    print("\n Проверяем связи в JSON:")
    customer_loaded = store_from_json.customers[0]
    print(f"   Покупатель: {customer_loaded.name}")
    print(f"   Куплено книг: {len(customer_loaded.purchased_books)}")
    if customer_loaded.purchased_books:
        print(f"   Первая книга: {customer_loaded.purchased_books[0].title}")
        print(f"   Автор книги: {customer_loaded.purchased_books[0].author.name}")

    # ТЕСТ 2: Сохраняем и загружаем из XML
    print(" ТЕСТ 2: Работа с XML")

    # Сохраняем в XML
    FileHandler.save_to_xml_file(store, "data/books.xml")
    print(" Данные сохранены в data/books.xml")

    # Загружаем обратно из XML
    store_from_xml = FileHandler.load_from_xml_file("data/books.xml")
    print(" Данные загружены из XML")

    # Проверяем что все восстановилось
    print("\n  Данные после загрузки из XML:")
    print(f"   Авторов: {len(store_from_xml.authors)}")
    print(f"   Книг: {len(store_from_xml.books)}")
    print(f"   Покупателей: {len(store_from_xml.customers)}")
    print(f"   Заказов: {len(store_from_xml.orders)}")

    # Проверяем связи в XML
    print("\n Проверяем связи в XML:")
    customer_xml = store_from_xml.customers[0]
    print(f"   Покупатель: {customer_xml.name}")
    print(f"   Баланс: {customer_xml.balance} руб.")
    print(f"   Куплено книг: {len(customer_xml.purchased_books)}")

    if customer_xml.purchased_books:
        print(f"   Купленные книги:")
        for book in customer_xml.purchased_books:
            print(f"     - {book.title} ({book.price} руб.)")
            print(f"       Автор: {book.author.name}")

    # Проверяем заказы
    print("\n Заказы из XML:")
    for order in store_from_xml.orders:
        print(f"     Заказ #{order.order_id}:")
        print(f"     Покупатель: {order.customer.name}")
        print(f"     Статус: {order.status}")
        print(f"     Сумма: {order.total_price} руб.")
        print(f"     Книг в заказе: {len(order.books)}")
        for book in order.books:
            print(f"       - {book.title}")

    # ТЕСТ 3: Сравниваем данные из JSON и XML
    print(" ТЕСТ 3: Сравнение JSON и XML")

    # Проверяем что данные идентичны
    json_books = len(store_from_json.books)
    xml_books = len(store_from_xml.books)
    json_customers = len(store_from_json.customers)
    xml_customers = len(store_from_xml.customers)

    print(f"Книг в JSON: {json_books}, в XML: {xml_books} - {'Совпадает' if json_books == xml_books else 'Ошибка'}")
    print(
        f"Покупателей в JSON: {json_customers}, в XML: {xml_customers} - {'Совпадает' if json_customers == xml_customers else 'Ошибка'}")

    # Проверяем конкретные значения
    if store_from_json.books and store_from_xml.books:
        json_first_book = store_from_json.books[0]
        xml_first_book = store_from_xml.books[0]

        print(f"\nПервая книга в JSON: '{json_first_book.title}' за {json_first_book.price} руб.")
        print(f"Первая книга в XML: '{xml_first_book.title}' за {xml_first_book.price} руб.")
        print(f"Названия совпадают: {'Да' if json_first_book.title == xml_first_book.title else 'Нет'}")
        print(f"Цены совпадают: {'Да' if json_first_book.price == xml_first_book.price else 'Нет'}")

    # Проверяем счетчики ID
    print(f"\nСчетчики ID после загрузки:")
    print(f"  JSON - Следующий ID книги: {store_from_json._next_book_id}")
    print(f"  XML - Следующий ID книги: {store_from_xml._next_book_id}")
    print(f"  Совпадают: {'Да' if store_from_json._next_book_id == store_from_xml._next_book_id else 'Нет'}")

    print("\n Все тесты завершены! Работа с JSON и XML успешно проверена!")
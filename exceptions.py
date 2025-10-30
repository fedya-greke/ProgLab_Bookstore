class BookNotFound(Exception):
    """Книга не найдена"""
    def __init__(self, book_title):
        self.book_title = book_title
        super().__init__(f"Книга {book_title} не найдена")
class NotEnoughMoney(Exception):
    """Недостаточно денег"""
    def __init__(self, customer_name: str, balance: float, required_money: float):
        self.customer_name = customer_name
        self.balance = balance
        self.required_money = required_money
        super().__init__(f"У {customer_name} недостаточно средств для оплаты.\n"
                         f"Баланс: {balance}, к оплате {required_money}")
class InvalidPrice(Exception):
    """Неверная цена книги"""
    def __init__(self, price: float):
        self.price = price
        super().__init__(f"Цена книги указанов не верно: {price}")

from collections import deque
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
import time
import uuid


class DeliveryType(Enum):
    STANDARD = "Стандартна"
    EXPRESS = "Експрес"
    FRAGILE = "Крихка/Цінна"


class DeliveryStatus(Enum):
    CREATED = "Створено"
    IN_PROGRESS = "У процесі"
    DELIVERED = "Доставлено"
    EXPIRED = "Прострочено/Скасовано"


@dataclass
class Package:
    weight_kg: float
    description: str

    def __str__(self) -> str:
        return f"{self.description} ({self.weight_kg} кг)"

    def __repr__(self) -> str:
        return f"Package(weight_kg={self.weight_kg}, description='{self.description}')"


class Delivery:
    def __init__(self, package: Package, delivery_type: DeliveryType,
                 base_cost: float, estimated_days: int, created_at: date = None):
        self.__id = str(uuid.uuid4())[:8]
        self.package = package
        self.delivery_type = delivery_type
        self.status = DeliveryStatus.CREATED
        self.created_at = created_at or date.today()
        self.start_time = None
        self.base_cost = base_cost
        self.estimated_days = estimated_days

    @property
    def delivery_id(self) -> str:
        return self.__id

    @property
    def base_cost(self) -> float:
        return self.__base_cost

    @base_cost.setter
    def base_cost(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("Базова вартість повинна бути числом!")
        if value < 0:
            raise ValueError("Базова вартість не може бути від'ємною!")
        self.__base_cost = float(value)

    @property
    def estimated_days(self) -> int:
        return self.__estimated_days

    @estimated_days.setter
    def estimated_days(self, value: int):
        if not isinstance(value, int):
            raise TypeError("Термін доставки повинен бути цілим числом!")
        if value <= 0:
            raise ValueError("Термін доставки повинен бути більшим за 0 днів!")
        self.__estimated_days = value

    def calculate_final_cost(self) -> float:
        return round(self.__base_cost + self.package.weight_kg * 10.0, 2)

    def is_overdue(self, today: date = None) -> bool:
        if self.status is DeliveryStatus.DELIVERED:
            return False
        if self.status is DeliveryStatus.EXPIRED:
            return True
        elapsed_days = ((today or date.today()) - self.created_at).days
        return elapsed_days > self.__estimated_days

    def __str__(self) -> str:
        return (
            f"Доставка [{self.__id}] ({self.delivery_type.value}) | Статус: {self.status.value}\n"
            f"   Вантаж: {self.package} | Створено: {self.created_at} | "
            f"Термін: {self.__estimated_days} дн.\n"
            f"   Підсумкова вартість: {self.calculate_final_cost()} грн"
        )

    def __repr__(self) -> str:
        return (f"Delivery(id='{self.__id}', cost={self.calculate_final_cost()}, "
                f"days={self.__estimated_days})")

    def __lt__(self, other) -> bool:
        if not isinstance(other, Delivery):
            return NotImplemented
        return self.estimated_days < other.estimated_days

    def __eq__(self, other) -> bool:
        if not isinstance(other, Delivery):
            return False
        return self.calculate_final_cost() == other.calculate_final_cost()

    def __add__(self, extra_fee: float):
        if not isinstance(extra_fee, (int, float)):
            raise TypeError("Додавати можна лише числове значення сервісного збору!")
        if extra_fee < 0:
            raise ValueError("Збір не може бути від'ємним!")
        new_delivery = Delivery(self.package, self.delivery_type,
                                self.base_cost + extra_fee, self.estimated_days, self.created_at)
        new_delivery.status = self.status
        return new_delivery

    def __enter__(self):
        print(f"\n[Контекст-менеджер] Початок обробки доставки [{self.__id}]...")
        self.status = DeliveryStatus.IN_PROGRESS
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type is not None or duration > 2.0:
            self.status = DeliveryStatus.EXPIRED
            print(f"[Контекст-менеджер] ТАЙМАУТ ({duration:.2f}c). Статус: {self.status.value}")
            return True
        self.status = DeliveryStatus.DELIVERED
        print(f"[Контекст-менеджер] Завершено ({duration:.2f}c). Статус: {self.status.value}")
        return False


class LocalDelivery(Delivery):
    def __init__(self, package: Package, delivery_type: DeliveryType,
                 base_cost: float, estimated_days: int, city_zone: int, created_at: date = None):
        super().__init__(package, delivery_type, base_cost, estimated_days, created_at)
        self.city_zone = city_zone

    def calculate_final_cost(self) -> float:
        return round(self.base_cost + self.package.weight_kg * 12.0 + self.city_zone * 25.0, 2)

    def __str__(self) -> str:
        return f"[Локальна] {super().__str__()} | Міська зона: {self.city_zone}"


class InternationalDelivery(Delivery):
    def __init__(self, package: Package, delivery_type: DeliveryType,
                 base_cost: float, estimated_days: int, customs_fee: float, created_at: date = None):
        super().__init__(package, delivery_type, base_cost, estimated_days, created_at)
        self.customs_fee = customs_fee

    def calculate_final_cost(self) -> float:
        return round(self.base_cost + self.package.weight_kg * 45.0 + self.customs_fee, 2)

    def __str__(self) -> str:
        return f"[Міжнародна] {super().__str__()} | Митний збір: {self.customs_fee} грн"


class InvoiceCalculator:
    """Функтор: рахує суму до сплати та пам'ятає історію розрахунків."""

    EXPRESS_MARKUP = 0.2

    def __init__(self, fuel_rate: float, history_size: int = 5):
        if not isinstance(fuel_rate, (int, float)):
            raise TypeError("Паливна надбавка повинна бути числом!")
        if not 0 <= fuel_rate < 1:
            raise ValueError("Паливна надбавка має бути в межах [0; 1)!")
        self.fuel_rate = fuel_rate
        self.calls_count = 0
        self.total_revenue = 0.0
        self.history = deque(maxlen=history_size)

    def __call__(self, delivery: Delivery) -> float:
        if not isinstance(delivery, Delivery):
            raise TypeError("Розрахунок можливий лише для об'єкта Delivery!")
        invoice = delivery.calculate_final_cost() * (1 + self.fuel_rate)
        if delivery.delivery_type is DeliveryType.EXPRESS:
            invoice *= 1 + self.EXPRESS_MARKUP
        invoice = round(invoice, 2)
        self.calls_count += 1
        self.total_revenue = round(self.total_revenue + invoice, 2)
        self.history.append((delivery.delivery_id, invoice))
        return invoice

    @property
    def average_invoice(self) -> float:
        return round(self.total_revenue / self.calls_count, 2) if self.calls_count else 0.0


class ActiveDeliveryIterator:
    """Ітератор, який пропускає завершені та скасовані доставки."""

    ACTIVE_STATUSES = (DeliveryStatus.CREATED, DeliveryStatus.IN_PROGRESS)

    def __init__(self, deliveries: list):
        self.__deliveries = deliveries
        self.__index = 0

    def __iter__(self):
        return self

    def __next__(self) -> Delivery:
        while self.__index < len(self.__deliveries):
            delivery = self.__deliveries[self.__index]
            self.__index += 1
            if delivery.status in self.ACTIVE_STATUSES:
                return delivery
        raise StopIteration


class LogisticsManager:
    def __init__(self, fuel_rate: float = 0.08):
        self.__deliveries = []
        self.invoice_calculator = InvoiceCalculator(fuel_rate)

    def add_delivery(self, delivery: Delivery):
        self.__deliveries.append(delivery)
        print(f"\n[Успіх] Додано до менеджера:\n{delivery}")

    def __len__(self) -> int:
        return len(self.__deliveries)

    def __getitem__(self, index: int) -> Delivery:
        return self.__deliveries[index]

    def __iter__(self):
        return iter(sorted(self.__deliveries, key=lambda d: d.estimated_days))

    def active_deliveries(self) -> ActiveDeliveryIterator:
        return ActiveDeliveryIterator(self.__deliveries)

    def overdue_deliveries(self, today: date = None):
        for delivery in self.__deliveries:
            if delivery.is_overdue(today):
                yield delivery

    def paginate(self, page_size: int = 3):
        if not isinstance(page_size, int) or page_size <= 0:
            raise ValueError("Розмір сторінки має бути додатним цілим числом!")
        for start in range(0, len(self.__deliveries), page_size):
            yield self.__deliveries[start:start + page_size]


def read_number(prompt: str, cast=float):
    return cast(input(prompt).strip())


def read_delivery_data() -> tuple:
    description = input("Опис вантажу: ").strip()
    package = Package(read_number("Вага (кг): "), description)
    if package.weight_kg <= 0:
        raise ValueError("Вага вантажу має бути додатною!")
    types = list(DeliveryType)
    for number, kind in enumerate(types, 1):
        print(f"  {number}. {kind.value}")
    delivery_type = types[read_number("Тип доставки (номер): ", int) - 1]
    base_cost = read_number("Базова вартість (грн): ")
    estimated_days = read_number("Очікуваний термін (дн.): ", int)
    days_ago = read_number("Створено днів тому (0 — сьогодні): ", int)
    created_at = date.today() - timedelta(days=days_ago)
    return package, delivery_type, base_cost, estimated_days, created_at


def choose_delivery(manager: LogisticsManager) -> Delivery:
    number = read_number(f"Номер доставки (1-{len(manager)}): ", int)
    if not 1 <= number <= len(manager):
        raise ValueError("Доставки з таким номером не існує!")
    return manager[number - 1]


def print_header(title: str):
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def show_active(manager: LogisticsManager):
    print_header("АКТИВНІ ДОСТАВКИ (кастомний ітератор)")
    for delivery in manager.active_deliveries():
        print(delivery)
        print("-" * 40)


def show_invoice(manager: LogisticsManager):
    calculator = manager.invoice_calculator
    delivery = choose_delivery(manager)
    print(f"Сума до сплати: {calculator(delivery)} грн")
    print_header("СТАН ФУНКТОРА InvoiceCalculator")
    print(f"Кількість викликів: {calculator.calls_count}")
    print(f"Накопичена виручка: {calculator.total_revenue} грн")
    print(f"Середній рахунок:   {calculator.average_invoice} грн")
    print(f"Останні розрахунки: {list(calculator.history)}")


def show_overdue(manager: LogisticsManager):
    print_header("ПРОСТРОЧЕНІ ДОСТАВКИ (генератор)")
    overdue = manager.overdue_deliveries()
    print(f"Об'єкт генератора: {overdue}")
    for delivery in overdue:
        print(delivery)
        print("-" * 40)


def show_pages(manager: LogisticsManager):
    page_size = read_number("Розмір сторінки: ", int)
    print_header(f"ПАГІНАЦІЯ (генератор, по {page_size})")
    for number, page in enumerate(manager.paginate(page_size), 1):
        print(f"Сторінка {number}: {[d.delivery_id for d in page]}")


def complete_delivery(manager: LogisticsManager):
    delivery = choose_delivery(manager)
    seconds = read_number("Тривалість обробки (с): ")
    with delivery:
        time.sleep(seconds)


def main():
    manager = LogisticsManager()
    actions = {
        "3": show_active, "4": show_invoice, "5": show_overdue,
        "6": show_pages, "7": complete_delivery,
    }
    print("=== Система управління доставкою вантажів ===")
    while True:
        print("\nОберіть дію:")
        print("1. Додати локальну доставку")
        print("2. Додати міжнародну доставку")
        print("3. Активні доставки (ітератор)")
        print("4. Розрахувати суму до сплати (функтор)")
        print("5. Прострочені доставки (генератор)")
        print("6. Пагінація доставок (генератор)")
        print("7. Обробити доставку (контекст-менеджер)")
        print("8. Вийти з програми")
        choice = input("Ваш вибір (1-8): ").strip()
        try:
            if choice == "1":
                data = read_delivery_data()
                city_zone = read_number("Міська зона (1-5): ", int)
                manager.add_delivery(LocalDelivery(*data[:4], city_zone, data[4]))
            elif choice == "2":
                data = read_delivery_data()
                customs_fee = read_number("Митний збір (грн): ")
                manager.add_delivery(InternationalDelivery(*data[:4], customs_fee, data[4]))
            elif choice in actions:
                actions[choice](manager)
            elif choice == "8":
                print("Роботу завершено.")
                break
            else:
                print("Невірний вибір. Введіть число від 1 до 8.")
        except (ValueError, TypeError, IndexError) as error:
            print(f"[Помилка] {error}")


if __name__ == "__main__":
    main()

from dataclasses import dataclass
from enum import Enum
import uuid
import time

# 1. Перелічуваний тип (Enum)
class DeliveryType(Enum):
    STANDARD = "Стандартна"
    EXPRESS = "Експрес"
    FRAGILE = "Крихка/Цінна"

class DeliveryStatus(Enum):
    CREATED = "Створено"
    IN_PROGRESS = "У процесі"
    DELIVERED = "Доставлено"
    EXPIRED = "Прострочено/Скасовано"

# 2. Структура даних (dataclass)
@dataclass
class Package:
    """Сутність даних, яка описує параметр посилки"""
    weight_kg: float
    description: str

    def __str__(self) -> str:
        return f"{self.description} ({self.weight_kg} кг)"

    def __repr__(self) -> str:
        return f"Package(weight_kg={self.weight_kg}, description='{self.description}')"

# 3. Базовий клас
class Delivery:
    """Базовий клас доставки з магічними методами та контекстним менеджером"""

    def __init__(self, package: Package, delivery_type: DeliveryType, base_cost: float, estimated_days: int):
        self.__id = str(uuid.uuid4())[:8]
        self.package = package
        self.delivery_type = delivery_type
        self.status = DeliveryStatus.CREATED
        self.start_time = None

        # Виклик сетерів для валідації
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
        return round(self.__base_cost + (self.package.weight_kg * 10.0), 2)

    # --- Магічні методи рядкового представлення ---
    def __str__(self) -> str:
        return (
            f"Доставка [{self.__id}] ({self.delivery_type.value}) | Статус: {self.status.value}\n"
            f"   Вантаж: {self.package} | Термін: {self.__estimated_days} дн. | "
            f"Підсумкова вартість: {self.calculate_final_cost()} грн"
        )

    def __repr__(self) -> str:
        return f"Delivery(id='{self.__id}', cost={self.calculate_final_cost()}, days={self.__estimated_days})"

    # --- Перевантаження операторів порівняння (за терміновістю) ---
    def __lt__(self, other) -> bool:
        if not isinstance(other, Delivery):
            return NotImplemented
        # Менше днів = терміновіша доставка
        return self.estimated_days < other.estimated_days

    def __eq__(self, other) -> bool:
        if not isinstance(other, Delivery):
            return False
        return self.calculate_final_cost() == other.calculate_final_cost()

    # --- Магічний метод додавання (Математика бізнесу: сервісний збір) ---
    def __add__(self, extra_fee: float):
        if not isinstance(extra_fee, (int, float)):
            raise TypeError("Додавати можна лише числове значення сервісного збору!")
        if extra_fee < 0:
            raise ValueError("Збір не може бути від'ємним!")
        
        # Створюємо та повертаємо НОВИЙ екземпляр класу для безпеки даних
        new_delivery = Delivery(
            package=self.package,
            delivery_type=self.delivery_type,
            base_cost=self.base_cost + extra_fee,
            estimated_days=self.estimated_days
        )
        new_delivery.status = self.status
        return new_delivery

    # --- Протокол контекстного менеджера (with) ---
    def __enter__(self):
        print(f"\n[Контекст-менеджер] Початок обробки доставки [{self.__id}]...")
        self.status = DeliveryStatus.IN_PROGRESS
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - (self.start_time or time.time())
        
        # Імітація Time-Out (якщо обробка зайняла більше 2 секунд або виникла помилка)
        if exc_type is not None or duration > 2.0:
            self.status = DeliveryStatus.EXPIRED
            print(f"[Контекст-менеджер] ПОМИЛКА/ТАЙМАУТ (тривалість: {duration:.2f}с). Статус виставлено: {self.status.value}")
            if exc_val:
                print(f"   Деталі: {exc_val}")
            return True  # Перехоплюємо виключення всередині блоку згідно із завданням
        else:
            self.status = DeliveryStatus.DELIVERED
            print(f"[Контекст-менеджер] Обробку завершено успішно (тривалість: {duration:.2f}с). Статус виставлено: {self.status.value}")
            return False

# 4. Класи-нащадки
class LocalDelivery(Delivery):
    """Локальна доставка"""
    def __init__(self, package: Package, delivery_type: DeliveryType, base_cost: float, estimated_days: int, city_zone: int):
        super().__init__(package, delivery_type, base_cost, estimated_days)
        self.city_zone = city_zone

    def calculate_final_cost(self) -> float:
        return round(self.base_cost + (self.package.weight_kg * 12.0) + (self.city_zone * 25.0), 2)

    def __str__(self) -> str:
        return f"[Локальна] {super().__str__()} | Міська зона: {self.city_zone}"

class InternationalDelivery(Delivery):
    """Міжнародна доставка"""
    def __init__(self, package: Package, delivery_type: DeliveryType, base_cost: float, estimated_days: int, customs_fee: float):
        super().__init__(package, delivery_type, base_cost, estimated_days)
        self.customs_fee = customs_fee

    def calculate_final_cost(self) -> float:
        return round(self.base_cost + (self.package.weight_kg * 45.0) + self.customs_fee, 2)

    def __str__(self) -> str:
        return f"[Міжнародна] {super().__str__()} | Митний збір: {self.customs_fee} грн"

# 5. Клас-менеджер з ітерацією
class LogisticsManager:
    """Менеджер із підтримкою ітерації за терміновістю (__iter__)"""
    def __init__(self):
        self.__deliveries = []

    def add_delivery(self, delivery: Delivery):
        self.__deliveries.append(delivery)
        print(f"\n[Успіх] Додано до менеджера:\n{delivery}")

    def __len__(self) -> int:
        return len(self.__deliveries)

    def __getitem__(self, index: int) -> Delivery:
        return self.__deliveries[index]

    def __iter__(self):
        # Ітерація у порядку від найтерміновіших до найдовших (сотування за estimated_days)
        sorted_deliveries = sorted(self.__deliveries, key=lambda d: d.estimated_days)
        return iter(sorted_deliveries)

    def show_all(self):
        print("\n" + "=" * 60)
        print(" УСІ ЗАРЕЄСТРОВАНІ ДОСТАВКИ (СОРТУВАННЯ ЗА ТЕРМІНОВІСТЮ) ")
        print("=" * 60)
        if not self.__deliveries:
            print("Менеджер порожній.")
        # Використання __iter__
        for d in self:
            print(d)
            print("-" * 40)
        print("=" * 60)

# --- Блок демонстрації ---
if __name__ == "__main__":
    print("=== Система управління доставкою вантажів ===")
    manager = LogisticsManager()

    while True:
        print("\nОберіть дію:")
        print("1. Додати локальну доставку")
        print("2. Додати міжнародну доставку")
        print("3. Показати всі доставки (сорт за терміновістю)")
        print("4. Протестувати магічний метод __add__ (нарахувати сервісний збір)")
        print("5. Протестувати Контекстний Менеджер (зміна статусу та Time-Out)")
        print("6. Демонстрація __str__ vs __repr__")
        print("7. Вийти з програми")
        
        choice = input("Ваш вибір (1-7): ").strip()

        try:
            if choice in ("1", "2"):
                desc = input("Опис посилки: ").strip()
                weight = float(input("Вага (кг): "))
                days = int(input("Термін (днів): "))
                cost = float(input("Базова вартість (грн): "))

                print("Оберіть тип доставки:\n1. Стандартна\n2. Експрес\n3. Крихка/Цінна")
                t_choice = input("Вибір (1-3): ").strip()
                dtype = DeliveryType.EXPRESS if t_choice == "2" else (DeliveryType.FRAGILE if t_choice == "3" else DeliveryType.STANDARD)
                pkg = Package(weight_kg=weight, description=desc)

                if choice == "1":
                    zone = int(input("Міська зона (число): "))
                    delivery = LocalDelivery(pkg, dtype, cost, days, city_zone=zone)
                else:
                    fee = float(input("Митний збір (грн): "))
                    delivery = InternationalDelivery(pkg, dtype, cost, days, customs_fee=fee)

                manager.add_delivery(delivery)

            elif choice == "3":
                manager.show_all()

            elif choice == "4":
                if len(manager) == 0:
                    print("[Помилка] Спочатку додайте хоча б одну доставку!")
                else:
                    fee = float(input("Введіть розмір додаткового сервісного збору (грн): "))
                    old_del = manager[0]
                    new_del = old_del + fee  # Виклик __add__
                    print("\n--- Результат операції __add__ ---")
                    print(f"Початкова доставка (незмінна): {old_del.calculate_final_cost()} грн")
                    print(f"Нова доставка (з доданим збором): {new_del.calculate_final_cost()} грн")

            elif choice == "5":
                if len(manager) == 0:
                    print("[Помилка] Спочатку додайте хоча б одну доставку!")
                else:
                    target = manager[0]
                    print("\n--- 1. Сценарій успішного бронювання/обробки ---")
                    with target as active_del:
                        print(f"Доставка в обробці: {active_del.status.value}")
                        time.sleep(0.5)

                    print("\n--- 2. Сценарій Time-Out / Помилки в контексті ---")
                    with target as active_del:
                        print("Імітація збою/тривалої обробки...")
                        time.sleep(2.1)  # перевищує 2 секунди

            elif choice == "6":
                if len(manager) == 0:
                    print("[Помилка] Спочатку додайте хоча б одну доставку!")
                else:
                    d = manager[0]
                    print("\n--- Виклики __str__ та __repr__ ---")
                    print("1. Результат print(delivery) [__str__]:")
                    print(str(d))
                    print("\n2. Результат у колекції / repr(delivery) [__repr__]:")
                    print(repr(d))

            elif choice == "7":
                print("Завершення роботи програми.")
                break
            else:
                print("[Помилка] Некоректний вибір. Введіть число від 1 до 7.")

        except (ValueError, TypeError) as e:
            print(f"\n[Помилка валідації або введення даних]: {e}")
        except Exception as e:
            print(f"\n[Непередбачувана помилка]: {e}")
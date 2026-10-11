from dataclasses import dataclass
from enum import Enum
import uuid

# 1. Перелічуваний тип (Enum)
class DeliveryType(Enum):
    STANDARD = "Стандартна"
    EXPRESS = "Експрес"
    FRAGILE = "Крихка/Цінна"

# 2. Структура даних (dataclass)
@dataclass
class Package:
    """Сутність даних, яка описує параметр посилки"""
    weight_kg: float
    description: str

# 3. Базовий клас
class Delivery:
    """Базовий клас доставки (ієрархія класів)"""
    def __init__(self, package: Package, delivery_type: DeliveryType, base_cost: float, estimated_days: int):
        self.__id = str(uuid.uuid4())[:8]
        self.package = package
        self.delivery_type = delivery_type
        
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
        return self.__base_cost + (self.package.weight_kg * 10.0)

    def get_info(self) -> str:
        return (
            f"Доставка [{self.__id}] | Тип: {self.delivery_type.value} \n"
            f"Опис: {self.package.description} | Вага: {self.package.weight_kg} кг | "
            f"Термін: {self.__estimated_days} дн. | Вартість: {self.calculate_final_cost()} грн"
        )

# 4. Класи-нащадки
class LocalDelivery(Delivery):
    """Локальна доставка (нащадок 1)"""
    def __init__(self, package: Package, delivery_type: DeliveryType, base_cost: float, estimated_days: int, city_zone: int):
        super().__init__(package, delivery_type, base_cost, estimated_days)
        self.city_zone = city_zone

    def calculate_final_cost(self) -> float:
        return round(self.base_cost + (self.package.weight_kg * 12.0) + (self.city_zone * 25.0), 2)

    def get_info(self) -> str:
        return f"[Локальна] {super().get_info()} | Міська зона: {self.city_zone}"

class InternationalDelivery(Delivery):
    """Міжнародна доставка (нащадок 2)"""
    def __init__(self, package: Package, delivery_type: DeliveryType, base_cost: float, estimated_days: int, customs_fee: float):
        super().__init__(package, delivery_type, base_cost, estimated_days)
        self.customs_fee = customs_fee

    def calculate_final_cost(self) -> float:
        return round(self.base_cost + (self.package.weight_kg * 45.0) + self.customs_fee, 2)

    def get_info(self) -> str:
        return f"[Міжнародна] {super().get_info()} | Митний збір: {self.customs_fee} грн"

# 5. Клас-менеджер (Композиція)
class LogisticsManager:
    """Менеджер, що містить список об'єктів (Композиція)"""
    def __init__(self):
        self.__deliveries = []

    def add_delivery(self, delivery: Delivery):
        self.__deliveries.append(delivery)
        print(f"\n[Успіх] Додано до менеджера: {delivery.get_info()}")

    def show_all(self):
        print("\n" + "=" * 50)
        print(" УСІ ЗАРЕЄСТРОВАНІ ДОСТАВКИ В СИСТЕМІ ")
        print("=" * 50)
        if not self.__deliveries:
            print("Менеджер порожній.")
        for d in self.__deliveries:
            print(d.get_info())
        print("=" * 50)

# --- Блок демонстрації ---
if __name__ == "__main__":
    print("=== Система управління доставкою вантажів ===")
    manager = LogisticsManager()

    while True:
        print("\nОберіть дію:")
        print("1. Додати локальну доставку")
        print("2. Додати міжнародну доставку")
        print("3. Показати всі доставки")
        print("4. Вийти з програми")
        
        choice = input("Ваш вибір (1-4): ").strip()

        try:
            if choice == "1":
                print("\n--- Введення даних для Локальної доставки ---")
                desc = input("Опис посилки: ").strip()
                weight = float(input("Вага (кг): "))
                days = int(input("Термін (днів): "))
                cost = float(input("Базова вартість (грн): "))
                zone = int(input("Міська зона (число): "))

                print("\nОберіть тип доставки:")
                print("1. Стандартна\n2. Експрес\n3. Крихка/Цінна")
                t_choice = input("Вибір типу (1-3): ").strip()
                dtype = DeliveryType.STANDARD
                if t_choice == "2":
                    dtype = DeliveryType.EXPRESS
                elif t_choice == "3":
                    dtype = DeliveryType.FRAGILE

                pkg = Package(weight_kg=weight, description=desc)
                delivery = LocalDelivery(pkg, dtype, cost, days, city_zone=zone)
                manager.add_delivery(delivery)

            elif choice == "2":
                print("\n--- Введення даних для Міжнародної доставки ---")
                desc = input("Опис посилки: ").strip()
                weight = float(input("Вага (кг): "))
                days = int(input("Термін (днів): "))
                cost = float(input("Базова вартість (грн): "))
                fee = float(input("Митний збір (грн): "))

                print("\nОберіть тип доставки:")
                print("1. Стандартна\n2. Експрес\n3. Крихка/Цінна")
                t_choice = input("Вибір типу (1-3): ").strip()
                dtype = DeliveryType.STANDARD
                if t_choice == "2":
                    dtype = DeliveryType.EXPRESS
                elif t_choice == "3":
                    dtype = DeliveryType.FRAGILE

                pkg = Package(weight_kg=weight, description=desc)
                delivery = InternationalDelivery(pkg, dtype, cost, days, customs_fee=fee)
                manager.add_delivery(delivery)

            elif choice == "3":
                manager.show_all()

            elif choice == "4":
                print("Завершення роботи програми")
                break
            else:
                print("[Помилка] Некоректний вибір. Введіть число від 1 до 4.")

        except (ValueError, TypeError) as e:
            print(f"\n[Помилка валідації або введення даних]: {e}")
        except Exception as e:
            print(f"\n[Непередбачувана помилка]: {e}")
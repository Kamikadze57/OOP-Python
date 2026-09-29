from dataclasses import dataclass
import uuid


@dataclass
class Package:
    """Сутність даних, яка описує параметр посилки"""

    weight_kg: float
    description: str
    is_fragile: bool = False


class Delivery:
    """Клас із поведінкою, що представляє доставку вантажу"""

    def __init__(
        self,
        package: Package,
        estimated_days: int,
        base_cost: float,
    ):
        self.id = str(uuid.uuid4())[:8]
        self.package = package

        # Валідація запускається через сетери
        self.estimated_days = estimated_days
        self.base_cost = base_cost

    @property
    def estimated_days(self) -> int:
        """Гетер для отримання терміну доставки"""
        return self._estimated_days

    @estimated_days.setter
    def estimated_days(self, value: int) -> None:
        """Сетер із валідацією терміну доставки"""
        if not isinstance(value, int):
            raise TypeError("Термін доставки повинен бути цілим числом")
        if value <= 0:
            raise ValueError("Термін доставки повинен бути більшим за 0 днів")
        self._estimated_days = value

    @property
    def base_cost(self) -> float:
        """Гетер для отримання базової вартості"""
        return self._base_cost

    @base_cost.setter
    def base_cost(self, value: float) -> None:
        """Сетер із валідацією базової вартості"""
        if not isinstance(value, (int, float)):
            raise TypeError("Базова вартість повинна бути числом")
        if value < 0:
            raise ValueError("Базова вартість доставки не може бути від'ємною")
        self._base_cost = float(value)

    def calculate_total_cost(self) -> float:
        """Розрахунок підсумкової вартості з урахуванням крихкості вантажу"""
        cost = self._base_cost + (self.package.weight_kg * 15.0)
        if self.package.is_fragile:
            cost += 50.0
        return round(cost, 2)


if __name__ == "__main__":
    print("=== Система управління доставкою вантажів ===")

    try:
        # Введення даних для вантажу
        desc = input("Введіть опис вантажу: ").strip()
        weight = float(input("Введіть вагу (кг): "))
        is_fragile = input("Вантаж крихкий? (1 - так, 0 - ні): ").strip() == "1"

        # Введення даних для доставки
        days = int(input("Введіть термін доставки (днів): "))
        cost = float(input("Введіть базову вартість (грн): "))

        # Створення об'єктів
        package = Package(
            weight_kg=weight, description=desc, is_fragile=is_fragile
        )
        delivery = Delivery(
            package=package, estimated_days=days, base_cost=cost
        )

        # Виведення результату
        print(f"\nДоставку [{delivery.id}] успішно створено!")
        print(f"Опис: {delivery.package.description}")
        print(f"Вага: {delivery.package.weight_kg} кг")
        print(f"Термін: {delivery.estimated_days} дн.")
        print(f"Підсумкова вартість: {delivery.calculate_total_cost()} грн")

        # Інспекція внутрішнього стану об'єкта
        print("\nВнутрішній стан об'єкта (vars):")
        print(vars(delivery))

    except (ValueError, TypeError) as e:
        print(f"\nПомилка введення даних або валідації: {e}")
    except Exception as e:
        print(f"\nНепередбачувана помилка: {e}")
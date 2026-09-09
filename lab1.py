class SpeedCalculator:
    """Клас для обчислення швидкості руху."""

    def __init__(self, distance: float, time: float):
        self.distance = distance
        self.time = time

    @property
    def distance(self) -> float:
        return self.__distance

    @distance.setter
    def distance(self, value: float):
        if value <= 0:
            raise ValueError("Відстань має бути більшою за 0")
        self.__distance = float(value)

    @property
    def time(self) -> float:
        return self.__time

    @time.setter
    def time(self, value: float):
        if value <= 0:
            raise ValueError("Час має бути більшим за 0")
        self.__time = float(value)

    def calculate_speed(self) -> float:
        return self.__distance / self.__time



class AverageStream:
    """Клас для обчислення середнього значення двох вимірів."""

    def __init__(self, value1: float, value2: float):
        self.value1 = value1
        self.value2 = value2

    @property
    def value1(self) -> float:
        return self.__value1

    @value1.setter
    def value1(self, value: float):
        if value < 0:
            raise ValueError("Значення не може бути від'ємним")
        self.__value1 = float(value)

    @property
    def value2(self) -> float:
        return self.__value2

    @value2.setter
    def value2(self, value: float):
        if value < 0:
            raise ValueError("Значення не може бути від'ємним")
        self.__value2 = float(value)

    def calculate_average(self) -> float:
        return (self.__value1 + self.__value2) / 2



if __name__ == "__main__":
    print("---------------Розрахунок швидкості---------------")
    try:
        user_distance = float(input("Введіть відстань (км): "))
        user_time = float(input("Введіть час (год): "))

        speed_calc = SpeedCalculator(user_distance, user_time)
        print(f"Швидкість руху (км/г): {speed_calc.calculate_speed():.2f}")

    except ValueError as e:
        print(f"Помилка валідації або введення: {e}")
    except Exception as e:
        print(f"Виникла непередбачувана помилка: {e}")

    print("\n--------------Обчислення середнього значення--------------")
    try:
        val1 = float(input("Введіть перше значення: "))
        val2 = float(input("Введіть друге значення: "))

        stream = AverageStream(val1, val2)
        print(f"Середнє арифметичне: {stream.calculate_average():.2f}")

    except ValueError as e:
        print(f"Помилка валідації або введення: {e}")
    except Exception as e:
        print(f"Виникла непередбачувана помилка: {e}")
import math
import timeit
import unittest
from typing import Callable

# Импортируем нашу скомпилированную Cython-функцию
try:
    from integrate import integrate_cython
except ImportError:
    integrate_cython = None
    print("Внимание: модуль integrate не найден. Выполните 'python setup.py build_ext --inplace'")


# 1. Функция на чистом Python с аннотациями (PEP 484)
def integrate(f: Callable[[float], float], a: float, b: float, *, n_iter: int = 1000) -> float:
    """
    Вычисляет определенный интеграл методом левых прямоугольников.

    :param f: подынтегральная функция
    :param a: нижний предел интегрирования
    :param b: верхний предел интегрирования
    :param n_iter: количество итераций (точность метода)
    :return: приближенное значение интеграла
    """
    acc = 0.0
    step = (b - a) / n_iter
    for i in range(n_iter):
        acc += f(a + i * step) * step
    return acc


# 2. Юнит-тестирование (unittest)
class TestIntegration(unittest.TestCase):
    def test_known_integral(self):
        """Проверка на известном интеграле: sin(x) от 0 до pi равен 2"""
        result = integrate(math.sin, 0, math.pi, n_iter=100000)
        self.assertAlmostEqual(result, 2.0, places=3)

    def test_stability(self):
        """Проверка того, что точность растет с увеличением числа итераций"""
        res1 = integrate(lambda x: x ** 2, 0, 1, n_iter=1000)
        res2 = integrate(lambda x: x ** 2, 0, 1, n_iter=10000)
        self.assertNotEqual(res1, res2)


# 3. Основной блок выполнения
if __name__ == "__main__":
    # Запуск тестов
    print("--- Запуск юнит-тестов ---")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegration)
    unittest.TextTestRunner(verbosity=2).run(suite)

    # Замеры времени
    print("\n--- Замеры производительности (n_iter = 10^6) ---")
    n = 10 ** 6

    # Замер чистого Python
    t_py = timeit.timeit(lambda: integrate(math.cos, 0, math.pi / 2, n_iter=n), number=5)
    print(f"Python (5 запусков): {t_py:.5f} сек")

    # Замер Cython
    if integrate_cython:
        t_cy = timeit.timeit(lambda: integrate_cython(math.cos, 0, math.pi / 2, n), number=5)
        print(f"Cython (5 запусков): {t_cy:.5f} сек")
        print(f"Ускорение: {t_py / t_cy:.2f} раз")
    else:
        print("Cython не доступен для замера.")
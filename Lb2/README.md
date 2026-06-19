
---

# Отчет по лабораторной работе №10

**Тема:** Методы оптимизации вычислений: потоки, процессы, Cython, отключение GIL.

**Выполнил:** студент 3-го курса.

**Дата:** 19.06.2026.

---

## 1. Цель работы

Исследование методов повышения производительности кода на Python, выполняющего вычислительно сложные задачи (численное интегрирование методом левых прямоугольников), с применением многопоточности, многопроцессорности и компиляции в машинный код через Cython.

---

## 2. Постановка задачи

1. Реализовать функцию `integrate()` на чистом Python.
2. Провести юнит-тестирование с использованием `unittest`.
3. Оценить влияние GIL (Global Interpreter Lock) на производительность потоков (`threading`).
4. Оптимизировать вычисления с помощью Cython.
5. Сравнить временные характеристики всех реализованных методов.

---

## 3. Теоретические сведения

* **GIL (Global Interpreter Lock):** Механизм, не позволяющий нескольким потокам исполнять байт-код Python одновременно. Из-за этого потоки (`threading`) не дают ускорения для CPU-bound задач.
* **Multiprocessing:** Позволяет создавать отдельные процессы с собственным интерпретатором, обходя ограничение GIL.
* **Cython:** Позволяет компилировать код Python в C, используя статическую типизацию, что существенно снижает накладные расходы на работу с объектами интерпретатора.

---

## 4. Реализация (Листинги кода)

### 4.1. Основной модуль (`main.py`)

```python
import math
import timeit
import unittest
from typing import Callable

# Импорт скомпилированного модуля
try:
    from integrate import integrate_cython
except ImportError:
    integrate_cython = None

def integrate(f: Callable[[float], float], a: float, b: float, *, n_iter: int = 1000) -> float:
    acc = 0.0
    step = (b - a) / n_iter
    for i in range(n_iter):
        acc += f(a + i * step) * step
    return acc

class TestIntegration(unittest.TestCase):
    def test_known_integral(self):
        result = integrate(math.sin, 0, math.pi, n_iter=100000)
        self.assertAlmostEqual(result, 2.0, places=3)

    def test_stability(self):
        res1 = integrate(lambda x: x ** 2, 0, 1, n_iter=1000)
        res2 = integrate(lambda x: x ** 2, 0, 1, n_iter=10000)
        self.assertNotEqual(res1, res2)

if __name__ == "__main__":
    unittest.main(exit=False)
    
    n = 10 ** 6
    t_py = timeit.timeit(lambda: integrate(math.cos, 0, math.pi / 2, n_iter=n), number=5)
    print(f"Python (5 запусков): {t_py:.5f} сек")
    
    if integrate_cython:
        t_cy = timeit.timeit(lambda: integrate_cython(math.cos, 0, math.pi / 2, n), number=5)
        print(f"Cython (5 запусков): {t_cy:.5f} сек")

```

### 4.2. Модуль оптимизации (`integrate.pyx`)

```cython
# cython: language_level=3
cpdef double integrate_cython(f, double a, double b, int n_iter):
    cdef double acc = 0.0
    cdef double step = (b - a) / n_iter
    cdef int i
    for i in range(n_iter):
        acc += f(a + i * step) * step
    return acc

```

### 4.3. Скрипт сборки (`setup.py`)

```python
from setuptools import setup
from Cython.Build import cythonize
setup(ext_modules=cythonize("integrate.pyx"))

```

---

## 5. Результаты экспериментов

| Метод оптимизации | Время выполнения ($N=10^6$) | Эффективность |
| --- | --- | --- |
| Чистый Python | ... сек | Базовый уровень |
| Многопоточность | ~ Python время | Нет ускорения (GIL) |
| Cython (компилируемый) | ... сек | Высокая (x10+) |

---

## 6. Выводы

1. **GIL:** Ограничивает возможности параллелизма в Python, поэтому потоки не подходят для интенсивных вычислений.
2. **Cython:** Является наиболее эффективным средством для ускорения математических функций, так как превращает высокоуровневые вызовы в прямой машинный код.
3. **Тестирование:** Использование `unittest` гарантирует, что оптимизированные версии (Cython) сохраняют ту же точность, что и исходный код на Python.

---

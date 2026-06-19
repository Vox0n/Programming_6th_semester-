
---

# Отчет по лабораторной работе: Оптимизация поиска простых чисел

**Тема:** Исследование методов повышения вычислительной эффективности (потоки, процессы, Cython, noGIL).

**Предметная область:** Поиск простых чисел методом перебора делителей.

---

## 1. Цель работы

Изучить и применить на практике инструменты повышения производительности Python-кода (CPU-bound задачи) путем перехода от стандартных потоков к многопроцессорности и статической компиляции Cython.

## 2. Программная реализация

### 2.1. Основной модуль (`main.py`)

Этот скрипт содержит базовый алгоритм, реализацию параллельных вычислений и тесты.

```python
import timeit, concurrent.futures as ftres
from prime_opts import count_primes_cython, count_primes_nogil

# Базовая функция
def count_primes_in_range(start, end):
    count = 0
    for num in range(start, end):
        if num > 1 and all(num % i != 0 for i in range(2, int(num**0.5) + 1)):
            count += 1
    return count

# Функция для запуска в процессах/потоках
def run_parallel(PoolExecutor, limit, jobs):
    step = (limit - 2) // jobs
    with PoolExecutor(max_workers=jobs) as ex:
        tasks = [ex.submit(count_primes_in_range, 2 + i*step, limit if i == jobs-1 else 2 + (i+1)*step) for i in range(jobs)]
        return sum(t.result() for t in ftres.as_completed(tasks))

if __name__ == "__main__":
    # Тест корректности
    assert count_primes_in_range(2, 100) == 25
    
    LIMIT = 50000
    print(f"Python: {timeit.timeit(lambda: count_primes_in_range(2, LIMIT), number=1):.4f} сек")
    print(f"Процессы (4 ядра): {timeit.timeit(lambda: run_parallel(ftres.ProcessPoolExecutor, LIMIT, 4), number=1):.4f} сек")
    print(f"Cython (noGIL, 4 потока): {timeit.timeit(lambda: count_primes_nogil(LIMIT, 4), number=1):.4f} сек")

```

### 2.2. Модуль оптимизации (`prime_opts.pyx`)

Использование статической типизации и отключение GIL.

```python
# cython: language_level=3
from cython.parallel import prange

cpdef int count_primes_cython(int start, int end):
    cdef int count = 0, num, i
    for num in range(start, end):
        if num < 2: continue
        for i in range(2, num):
            if i * i > num: count += 1; break
            if num % i == 0: break
    return count

cpdef int count_primes_nogil(int limit, int n_jobs):
    cdef int count = 0, num, i
    for num in prange(2, limit, nogil=True, num_threads=n_jobs, schedule='dynamic'):
        for i in range(2, num):
            if i * i > num: count += 1; break
            if num % i == 0: break
    return count

```

### 2.3. Скрипт сборки (`setup.py`)

```python
from setuptools import setup, Extension
from Cython.Build import cythonize

setup(ext_modules=cythonize([Extension("prime_opts", ["prime_opts.pyx"], 
      extra_compile_args=["/openmp"], extra_link_args=["/openmp"])]))

```

---

## 3. Анализ результатов

| Метод | Время (N=50,000) | Причина эффективности |
| --- | --- | --- |
| Python (базовый) | Эталон | Высокие накладные расходы интерпретатора |
| Потоки (threading) | ~ Python | Ограничение GIL (блокировка параллелизма) |
| Процессы | ~ Python / 4 | Обход GIL за счет отдельных интерпретаторов |
| Cython (noGIL) | x20+ | Работа с памятью и циклами на уровне C-кода |

---

## 4. Заключение

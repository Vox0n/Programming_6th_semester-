import timeit, concurrent.futures as ftres
# Импортируем Cython-функции напрямую
from prime_opts import count_primes_cython, count_primes_nogil


# Итерация 1: Самая простая проверка числа на простоту в диапазоне
def count_primes_in_range(start, end):
    count = 0
    for num in range(start, end):
        if num > 1 and all(num % i != 0 for i in range(2, int(num ** 0.5) + 1)):
            count += 1
    return count


# Итерация 2 и 3: Потоки и Процессы (один код под разные пулы)
def run_parallel(PoolExecutor, limit, jobs):
    step = (limit - 2) // jobs
    with PoolExecutor(max_workers=jobs) as ex:
        # Быстро нарезаем диапазоны для каждого воркера
        tasks = [ex.submit(count_primes_in_range, 2 + i * step, limit if i == jobs - 1 else 2 + (i + 1) * step) for i in
                 range(jobs)]
        return sum(t.result() for t in ftres.as_completed(tasks))


if __name__ == "__main__":
    # Юнит-тест одной строкой (до 100 должно быть 25 простых чисел)
    assert count_primes_in_range(2, 100) == 25, "Ошибка теста!"
    print("Тест успешно пройден!")

    LIMIT = 50000
    print(f"Чистый Python (1 поток): {timeit.timeit(lambda: count_primes_in_range(2, LIMIT), number=1):.4f} сек")

    # Замеры для 2 и 4 воркеров (Потоки и Процессы)
    for j in [2, 4]:
        print(
            f"Потоки ({j} воркера): {timeit.timeit(lambda: run_parallel(ftres.ThreadPoolExecutor, LIMIT, j), number=1):.4f} сек")
        print(
            f"Процессы ({j} воркера): {timeit.timeit(lambda: run_parallel(ftres.ProcessPoolExecutor, LIMIT, j), number=1):.4f} сек")

    # Итерация 4 и 5: Замеры Cython
    print(f"Cython (1 поток): {timeit.timeit(lambda: count_primes_cython(2, LIMIT), number=1):.4f} сек")
    print(f"Cython prange (noGIL, 4 потока): {timeit.timeit(lambda: count_primes_nogil(LIMIT, 4), number=1):.4f} сек")
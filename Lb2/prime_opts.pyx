# cython: language_level=3
# cython: annotate=True
from cython.parallel import prange

# Итерация 4: Базовый Cython
cpdef int count_primes_cython(int start, int end):
    cdef int count = 0, num, i
    for num in range(start, end):
        if num < 2: continue
        for i in range(2, num):
            if i * i > num: count += 1; break
            if num % i == 0: break
    return count

# Итерация 5: Cython с prange (noGIL)
cpdef int count_primes_nogil(int limit, int n_jobs):
    cdef int count = 0, num, i
    for num in prange(2, limit, nogil=True, num_threads=n_jobs, schedule='dynamic'):
        for i in range(2, num):
            if i * i > num: count += 1; break
            if num % i == 0: break
    return count
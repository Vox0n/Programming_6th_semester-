# integrate.pyx
# cython: language_level=3

# cdef объявляет переменные на уровне C, что дает ускорение
cpdef double integrate_cython(f, double a, double b, int n_iter):
    cdef double acc = 0.0
    cdef double step = (b - a) / n_iter
    cdef int i
    cdef double x
    
    # Цикл выполняется на скорости C
    for i in range(n_iter):
        x = a + i * step
        acc += f(x) * step
    return acc
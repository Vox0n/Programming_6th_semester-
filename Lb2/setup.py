from setuptools import setup, Extension
from Cython.Build import cythonize

setup(
    ext_modules=cythonize([Extension("prime_opts", ["prime_opts.pyx"], extra_compile_args=["/openmp"], extra_link_args=["/openmp"])], annotate=True)
)
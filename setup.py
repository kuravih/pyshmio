from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        "pyshmio",
        sources=["src/bindings.cpp"],
        include_dirs=[
            pybind11.get_include(),
            "src/lib",
        ],
        language="c++",
        extra_compile_args=["-std=c++20"],
    ),
]

setup(
    name="pyshmio",
    version="0.0.1",
    description="Python bindings for shmio shared memory io",
    ext_modules=ext_modules,
    zip_safe=False,
)

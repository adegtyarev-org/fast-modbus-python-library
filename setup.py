
from setuptools import setup, find_packages

setup(
    name="FastModbusLibrary",
    version="0.1.0",
    description="Library for fast Modbus device communication, supporting scanning, event handling, and register operations.",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=["pyserial"],  # Убедимся, что pyserial установлен для работы с Modbus
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

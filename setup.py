from setuptools import setup, find_packages

setup(
    name='fastmodbuslibrary',
    version='0.1.3',
    packages=find_packages(),
    install_requires=[
        'pyserial',
    ],
    entry_points={
        'console_scripts': [
            'modbus_scan = fastmodbuslibrary.fast_modbus_scanner:main',
            'modbus_events = fastmodbuslibrary.fast_modbus_events:main',
            'modbus_config_events = fastmodbuslibrary.fast_modbus_config_events:main',
            'modbus_client = fastmodbuslibrary.fast_modbus_client:main',
        ],
    },
    author='Aleksandr Degtyarev',
    author_email='adegtyarev.ap@gmail.com',
    description='Modbus tools for Wirenboard devices',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/aadegtyarev/fast-modbus-python-library',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)

from setuptools import setup, find_packages

setup(
    name='IrohUI',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'PyQt6>=6.0.0',
        'requests>=2.25.0',
        'sendme-iroh>=0.1.0'  # Replace with actual package if available
    ],
    entry_points={
        'console_scripts': [
            'irohui=irohui.main:main'
        ]
    },
    include_package_data=True,
    description='A cross-platform UI for the Sendme Iroh protocol built with Python and PyQt.',
    author='Aaron',
    license='MIT'
)
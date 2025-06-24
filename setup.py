from setuptools import setup, find_packages

setup(
    name="Python-IDE",
    version="0.1.0",
    description="A minimal Python IDE with execution tracking and chart output",
    author="Your Name",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "jedi",
        "matplotlib",  # or any other charting lib you want to support
        "pillow",
    ],
    entry_points={
        "console_scripts": [
            "Python-IDE=main:Python-IDE/python_ide",
        ],
    },
    python_requires=">=3.7",
)

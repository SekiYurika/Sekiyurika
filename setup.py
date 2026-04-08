from setuptools import setup, find_packages

setup(
    name="yurika-options-toolkit",
    version="1.0.0",
    author="Yurika Seki",
    description="Professional options trading analysis toolkit",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0", 
        "yfinance>=0.1.70",
        "requests>=2.25.0",
        "matplotlib>=3.5.0",
        "scipy>=1.7.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3",
    ],
)

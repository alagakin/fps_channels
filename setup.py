from setuptools import setup, find_packages

setup(
    name="fps_channels",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot==13.9",
        "pandas==1.3.5",
        "dataframe-image==0.1.5",
        "tenacity==8.2.3",
        "lxml==4.9.2",
        "openpyxl==3.1.1",
    ]
)

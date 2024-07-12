import os

from setuptools import setup, find_packages


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setup(
    name="fps_channels",
    version="1.4",
    packages=find_packages(),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    install_requires=[
        "pandas~=2.1.3",
        "dataframe-image~=0.2.3",
        "tenacity~=8.2.3",
        "lxml~=5.1.0",
        "openpyxl~=3.1.2",
        "aiohttp~=3.9.5",
        "requests~=2.32.3"
    ]
)

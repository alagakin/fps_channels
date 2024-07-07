import os

from setuptools import setup, find_packages


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setup(
    name="fps_channels",
    version="1.2",
    packages=find_packages(),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    install_requires=[
        "pandas~=1.3.5",
        "dataframe-image~=0.1.5",
        "tenacity~=8.2.3",
        "lxml~=4.9.2",
        "openpyxl~=3.1.1",
        "aiohttp~=3.9.5",
        "requests~=2.32.3"
    ]
)

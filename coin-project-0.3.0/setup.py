# -*- coding=utf-8 -*-
from setuptools import setup, find_packages

__version__ = '0.3.0'


setup(
    name="coin-project",
    version=__version__,
    packages=find_packages(exclude=["tests.*", "tests", "docs", "scripts", "static"]),
    install_requires=['websocket-client', 'requests', 'redis', 'certifi', 'six', 'sqlalchemy',
                      'pymysql', 'pycrypto', 'commandr'],
    platforms='any',
    include_package_data=True,
    zip_safe=False,
    entry_points={},
)

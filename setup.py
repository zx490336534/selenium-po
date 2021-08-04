# -*- coding: utf-8 -*-
# @Time    : 2020/8/22 10:26 上午
# @Author  : zhongxin
# @Email   : 490336534@qq.com
# @File    : setup.py

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='selenium-po',
    version='0.0.7',
    description='使用yaml实现selenium的po',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    author='zhong xin',
    author_email='490336534@qq.com',
    url='https://github.com/zx490336534/selenium-po',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['PyYAML', 'selenium']
)

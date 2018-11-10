# -*- coding: utf-8 -*-
from setuptools import setup


setup(
    entry_points={
        'console_scripts': [
            'rst2txt = rst2txt:main',
        ],
    },
    use_scm_version=True,
)

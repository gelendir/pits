#!/usr/bin/env python
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = [l.strip() for l in f]

with open('README.md') as f:
    long_desc = f.read().strip()

setup(
    name='PiTS',
    version='0.1',
    url='http://github.com/gelendir/pits',
    license='GPL3',
    author='Gregory Eric Sanderson',
    author_email='gregory.eric.sanderson@gmail.com',
    description='Piano-To-Speech',
    long_description=long_desc,
    packages=find_packages(),
    zip_safe=False,
    package_data={
        'pits.assets': ['*']
    },
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'pits_play = pits.play:main',
        ]
    }
)

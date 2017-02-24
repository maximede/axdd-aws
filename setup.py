import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='awslogin',
    version='1.0',
    packages=['awslogin'],
    include_package_data=True,
    install_requires = [
        'boto',
        'requests',
        'bs4'
    ],
    license='Apache License, Version 2.0',
    description='',
    long_description=README,
    url='https://github.com/uw-it-aca/axdd-aws',
    author = "UW-IT AXDD",
    author_email = "aca-it@uw.edu",
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)

#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='ppp_libmodule',
    version='0.7.7',
    description='Library for writing Python modules for the PPP.',
    url='https://github.com/ProjetPP/PPP-libmodule-Python',
    author='Valentin Lorentz',
    author_email='valentin.lorentz+ppp@ens-lyon.org',
    license='MIT',
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Libraries',
    ],
    install_requires=[
        'ppp_datamodel>=0.6,<0.7',
    ],
    packages=[
        'ppp_libmodule',
    ],
)



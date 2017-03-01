# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from shortener_url.version import version_str

setup(
    name='shortener-url',
    version=version_str(),
    description='Url Shortener',
    author='S2LTIC Team',
    url='https://github.com/srault95/shortener-url',
    zip_safe=False,
    license='AGPLv3',
    include_package_data=True,
    packages=find_packages(),
    test_suite='nose.collector',
    tests_require=[
      'nose',
    ],
)

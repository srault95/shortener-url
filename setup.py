# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from shortener.version import version_str

setup(
    name='mongo-url-shortener',
    version=version_str(),
    description='Url Shortener with MongoDB',
    author='S2LTIC Team',
    url='https://github.com/srault95/mongo-url-shortener',
    zip_safe=False,
    license='AGPLv3',
    include_package_data=True,
    packages=find_packages(),
    test_suite='nose.collector',
    tests_require=[
      'nose',
    ],
)

from setuptools import setup, find_packages

setup(
    name='soldat_extmod_api',
    version='0.2.1',
    packages=find_packages(),
    install_requires=[
        'keystone_engine>=0.9.2',
        'pefile>=2023.2.7',
        'pywin32>=306'
    ],
    package_data={'': ['**/*.asm']},
)

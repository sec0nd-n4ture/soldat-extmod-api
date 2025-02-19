from setuptools import setup, find_packages

setup(
    name='soldat_extmod_api',
    version='0.0.8',
    packages=find_packages(),
    install_requires=[
        'keystone_engine>=0.9.2',
        'pefile>=2023.2.7',
        'pynput>=1.7.6',
        'pywin32>=306'
    ],
    package_data={'': ['**/*.asm']},
)

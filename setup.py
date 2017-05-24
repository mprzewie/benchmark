from setuptools import setup

setup(
    name='benchmark',
    version='1.0',
    description='A module for calculating complexities of functions',
    author='Marcin Przewiezlikowski',
    author_email='m.przewie@gmail.com',
    license='MIT',
    packages=['benchmark'],  # same as name'
    install_requires=['numpy', 'matplotlib', 'stopit'],  # external packages as dependencies
    entry_points={
        'console_scripts': ['benchmark = benchmark.blehmark:blehmark']
    }

)

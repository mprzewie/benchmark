from setuptools import setup

setup(
   name='benchmark',
   version='1.0',
   description='A module for calculating complexities of functions',
   author='Marcin Przewięźlikowski',
   author_email='m.przewie@gmail.com',
   packages=['benchmark'],  #same as name
   install_requires=['numpy', 'matplotlib'], #external packages as dependencies
)
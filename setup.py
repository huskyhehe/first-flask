from setuptools import find_packages, setup

setup(
    name='flaskr',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)

'''
packages 
    tells Python what package directories (and the Python files they contain) to include. 
find_packages() 
    finds these directories automatically so you don’t have to type them out. 
include_package_data
   is set True To include other files, such as the static and templates directories.
    Python needs another file named MANIFEST.in to tell what this other data is.
'''

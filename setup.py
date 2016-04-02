from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cockatiel',
    version='0.0.1',
    description='Simple replicated file storage',
    long_description=long_description,
    url='https://github.com/raphaelm/cockatiel',
    author='Raphael Michel',
    author_email='mail@raphaelmichel.de',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='django file storage media backend replicated',
    install_requires=[
        'aiohttp>=0.21,<0.22', 'cchardet',
    ],
    extras_require={
        'dev': ['requests', 'pytest', 'flake8'],
    },

    packages=find_packages(exclude=['unit_tests', 'unit_tests.*', 'functional_tests', 'functional_tests.*']),
    include_package_data=True,
)

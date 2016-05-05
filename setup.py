import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

VERSION = __import__("supermigrate").__version__

setup(
    name='django-supermigrate',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='package to manage migrations on production and development environment simultaneously',
    long_description=README,
    url='https://github.com/paytm/django-supermigrate',
    author='Shrey Agarwal, Taranjeet Singh',
    author_email='shrey.agarwal@paytm.com, reachtotj@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django :: 1.8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Framework :: Django :: 1.8',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
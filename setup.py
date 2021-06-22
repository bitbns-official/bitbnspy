from sys import version_info
from setuptools import setup

import pkg_resources
from os import path

if version_info.major == 3 and version_info.minor < 6 or \
    version_info.major < 3:
    print("Your python interpreter must be 3.6 or greater!")
    exit(1)

this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, 'CHANGELOG.txt')) as f:
    long_description = f.read()

with open(path.join(this_directory, 'README.md')) as f:
    long_description += "\n" + f.read()

with open(path.join(this_directory, 'requirements.txt')) as f:
    requirements = f.read().splitlines()

setup(
    name='bitbnspy',
    packages=['bitbnspy'],
    version='0.2.1',
    license='MIT',
    description='This project is designed to assist you make your own projects that interact with the Bitbns API. '
                'This project seeks to have complete API coverage and WebSockets',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Prashant Singh',
    author_email='prashant@buyhatke.com',
    url='https://github.com/bitbns-official/bitbnspy',
    # download_url='https://github.com/bitbns-official/bitbnspy/archive/0.1.tar.gz',
    keywords=['python', 'bitbns', 'DEFI', 'crypto', 'btc', 'eth', 'neo', 'orderbook', 'crypto trading', 'bitbns api'],
    install_requires=requirements,
    package_dir={"": "src"},
    classifiers=[
        'Development Status :: 4 - Beta',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.6'
    ],
    python_requires=">=3.6",
)

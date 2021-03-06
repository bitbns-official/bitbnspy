from setuptools import setup

import pkg_resources


from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

# with open(path.join(this_directory, 'requirements.txt')) as requirements_txt:
#     install_requires = [
#         str(requirement)
#         for requirement
#         in pkg_resources.parse_requirements(requirements_txt)
#     ]

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='bitbnspy',
    packages=['bitbnspy'],
    version='0.1.32',
    license='MIT',
    description='This project is designed to assist you make your own projects that interact with the Bitbns API. '
                'This project seeks to have complete API coverage excluding WebSockets which would be released in '
                'the future version.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Prashant Singh',
    author_email='prashant@buyhatke.com',
    url='https://github.com/bitbns-official/bitbnspy',
    download_url='https://github.com/bitbns-official/bitbnspy/archive/0.1.tar.gz',
    keywords=['npm', 'bitbns', 'crypto', 'btc', 'eth', 'neo', 'orderbook', 'crypto trading', 'bitbns api'],
    install_reqs=requirements,
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
)

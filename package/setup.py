from distutils.core import setup

setup(
    name='bitbns',
    packages=['bitbns'],
    version='0.1',
    license='MIT',
    description='This project is designed to assist you make your own projects that interact with the Bitbns API. '
                'This project seeks to have complete API coverage excluding WebSockets which would be released in '
                'the future version.',
    author='Prashant Singh',
    author_email='prashant@buyhatke.com',
    url='https://github.com/bitbns-official/python-bitbns-api',
    # Provide either the link to your github or to your website
    download_url='https://github.com/bitbns-official/python-bitbns-api/archive/0.1.tar.gz',
    keywords=['npm', 'bitbns', 'crypto', 'btc', 'eth', 'neo', 'orderbook', 'crypto trading', 'bitbns api'],
    install_requires=[  # I get to this in a second
        'validators',
        'beautifulsoup4',
        'requests',
        'socketio',
        'time',
        'base64',
        'hashlib',
        'hmac',
        'json',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.6',
    ],
)

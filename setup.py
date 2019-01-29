from setuptools import setup

setup(
    name='amirich',
    version='0.1',
    py_modules=['amirich'],
    install_requires=[
        'Click',
        'requests',
        'pandas'
    ],
    entry_points='''
        [console_scripts]
        amirich=amirich:cli
    ''',
)

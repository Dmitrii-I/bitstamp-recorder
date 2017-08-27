""" See [1] on how to write proper `setup.py` script.

[1] https://github.com/pypa/sampleproject/blob/master/setup.py
"""


from setuptools import find_packages, setup
from websocket_recorder import __version__


setup(
    name='websocket_recorder',
    version=__version__,
    description='Record messages from a websocket into a gzip-compressed file',
    long_description='Record messages from a websocket into a gzip-compressed file.',
    url='None',
    author='Dmitrii Izgurskii',
    author_email='izgurskii@gmail.com',
    license='Proprietary',
    keywords='websockets',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*', 'build'])
)

from pathlib import Path
from setuptools import setup

_classifiers = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Topic :: Software Development :: Libraries',
    'Topic :: Utilities',
]


def _version():
    with open('wavemap/__init__.py') as fp:
        line = next(i for i in fp if i.startswith('__version__'))
        return line.strip().split()[-1].strip("'")


REQUIREMENTS = Path('requirements.txt').read_text().splitlines()


if __name__ == '__main__':
    setup(
        name='wavemap',
        version=_version(),
        author='Tom Ritchford',
        author_email='tom@swirly.com',
        url='https://github.com/rec/wavemap',
        py_modules=['wavemap'],
        description='Memory map WAVE or raw audio files',
        long_description=open('README.rst').read(),
        license='MIT',
        classifiers=_classifiers,
        keywords=['testing', 'modules'],
        install_requires=REQUIREMENTS,
    )

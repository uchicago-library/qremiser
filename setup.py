from setuptools import setup, find_packages

def readme():
    with open("README.md", 'r') as f:
        return f.read()

setup(
    name = "qremiser",
    description = "An RPC-like endpoint for producing qremis records",
    long_description = readme(),
    packages = find_packages(
        exclude = [
        ]
    ),
    # We need the git version of python-magic for it to work in certain docker
    # configurations. See:
    # https://github.com/ahupp/python-magic/commit/ee09e35780c8d898bfb8913e847eff5eac38ffd2
    # which hasn't made its way into pip yet.
    dependency_links = [
        'https://github.com/uchicago-library/pyqremis' +
        '/tarball/master#egg=pyqremis',
        'https://github.com/uchicago-library/nothashes' +
        '/tarball/master#egg=nothashes',
        'https://github.com/ahupp/python-magic' +
        '/tarball/master#egg=python-magic'
    ],
    install_requires = [
        'flask>0',
        'flask_restful',
        'python-magic',
        'pyqremis',
        'nothashes',
    ],
)

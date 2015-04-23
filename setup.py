from setuptools import find_packages, setup

# PyPI only supports nicely-formatted README files in reStructuredText.
# Newsapps seems to prefer Markdown.  Use a version of the pattern from
# https://coderwall.com/p/qawuyq/use-markdown-readme-s-in-python-modules
# to convert the Markdown README to rst if the pypandoc package is
# present.
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError, OSError):
    long_description = open('README.md').read()

# Load the version from the version module
exec(open('chicago/version.py').read())

setup(
    name='chicago',
    version=__version__,
    author='Geoff Hing for the Chicago Tribune News Applications Team',
    author_email='geoffhing@gmail.com',
    url='https://github.com/newsapps/python-chicago',
    description='Chicago meta information and other fun stuff',
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    install_requires=[
    ],
    tests_require=[
        'nose',
    ],
    test_suite='nose.collector',
    keywords=['chicago', 'geography', 'city'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)

from setuptools import setup

version = '0.6.0'

setup(
    name='Git2SC',
    version=version,
    description='Synchronize documentation on git to Confluence',
    author='jamatute',
    author_email='jamatute@paradigmadigital.com',
    packages=['git2sc', ],
    license='GPLv2',
    long_description=open('README.md').read(),
    entry_points={
      'console_scripts': ['git2sc = git2sc:main']}
)

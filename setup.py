import sys
import warnings

try:
    from setuptools import setup
except ImportError:
    try:
        from setuptools.core import setup
    except ImportError:
        from distutils.core import setup

from distutils.core import setup, Extension
import os

MAJOR = 0
MINOR = 5
MICRO = 0
ISRELEASED = False
SNAPSHOT = False
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)
QUALIFIER = ''

FULLVERSION = VERSION
print(FULLVERSION)

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

if not ISRELEASED:
    import subprocess
    FULLVERSION += '.dev'
    if SNAPSHOT:
        pipe = None
        for cmd in ['git', 'git.cmd']:
            try:
                pipe = subprocess.Popen([cmd, "describe", "--always",
                                         "--match", "v[0-9\/]*"],
                                        stdout=subprocess.PIPE)
                (so, serr) = pipe.communicate()
                print(so, serr)
                if pipe.returncode == 0:
                    pass
                print('here')
            except:
                pass
            if pipe is None or pipe.returncode != 0:
                warnings.warn("WARNING: Couldn't get git revision, "
                              "using generic version string")
            else:
                rev = so.strip()
                # makes distutils blow up on Python 2.7
                if sys.version_info[0] >= 3:
                    rev = rev.decode('ascii')

                # use result of git describe as version string
                FULLVERSION = VERSION + '-' + rev.lstrip('v')
                break
else:
    FULLVERSION += QUALIFIER

setup(
    name='metadatastore',
    version=FULLVERSION,
    author='Arkilic',
    author_email=None,
    license="BSD (3-clause)",
    url="https://github.com/NSLS-II/metadatastore",
    packages=['metadatastore', 'metadatastore.utest', 'metadatastore.utils',
              'metadatastore.examples', 'metadatastore.examples.sample_data'],
    long_description=read('README.md'),
    classifiers=[
        "License :: OSI Approved :: EPICS License",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2.7.9",
    ],
)

from distutils.core import setup
from distutils.core import Extension



# TODO: get ARMNLIB variable from the environment and compile the rmn_wrapper


import sys

import os

armnlib = "ARMNLIB"
armnlib_path = ""



libraries = ["rmn"]
library_dirs = []

includes = []


if armnlib in os.environ:
    print os.environ[armnlib]
    armnlib_path = os.environ[armnlib]

    ec_arch = os.environ["EC_ARCH"]

    # get includes
    path1 = os.path.join(armnlib_path, "include")
    path1_lib = os.path.join(armnlib_path, "lib")

    # add search directories for headers
    includes.append(path1)
    includes.append(os.path.join(path1, ec_arch))

    # add library search directories
    #library_dirs.append()
    library_dirs.append(os.path.join(path1_lib, ec_arch))

else:
    raise Exception("ARMNLIB variable is not defined")

module_wrap = Extension(
    "rpn.libpyrmn",
    include_dirs=includes,
    libraries=libraries,
    library_dirs=library_dirs,
    sources=["rmn_wrapper.c"])

setup(
    name='pyrmnlib',
    version='0.0.1',
    packages=['rpn', 'rpn.tests', 'rpn_use_examples'],
    package_dir={'': 'src'},
    url='',
    license='',
    author='huziy',
    author_email='guziy.sasha@gmail.com',
    description='', requires=['numpy'],
    #ext_modules=[module_wrap]
    # well, it is not ready yet for pgi so the extension should be installed separately
)

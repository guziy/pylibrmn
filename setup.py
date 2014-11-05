from distutils.core import setup
from distutils.core import Extension



# TODO: get ARMNLIB variable from the environment and compile the rmn_wrapper


import sys

import os

armnlib = "ARMNLIB"
armnlib_path = ""

native_lib_filename = "libpyrmn.so"

##build native library using the Makefile
import subprocess
subprocess.call(["make"])
if os.path.isfile(native_lib_filename):
    print "The '{0}' was created. Now you need to add '{1}' to LD_LIBRARY_PATH variable, or put the compiled file" \
          "into one of the folders from the list in your current LD_LIBRARY_PATH" \
          "".format(native_lib_filename, os.getcwd())
    print "The list of folders in your current LD_LIBRARY_PATH: "
    print "--" * 10 + "- Start ----------"
    for fi in os.environ["LD_LIBRARY_PATH"].split(":"):
       print fi
    print "--" * 10 + "- End   ----------"
else:
    raise Exception("Failed to build '{0}'".format(native_lib_filename))


#raise Exception("ARMNLIB variable is not defined")

#module_wrap = Extension(
#    "rpn.libpyrmn",
#    include_dirs=includes,
#    libraries=libraries,
#    library_dirs=library_dirs,
#    sources=["rmn_wrapper.c"])


long_description = """
Requires ssm environment and shared version of the fortran version of rmnlib. Works only on linux..
Written for python 2.7.x and not compatible with python3 yet.  
"""
setup(
    name='pylibrmn',
    version='0.0.1',
    packages=['rpn', 'rpn.util', 'rpn.domains', 'rpn.tests', 'rpn_use_examples'],
    package_dir={'': 'src'},
    url='',
    license='GPL',
    author='huziy',
    author_email='guziy.sasha@gmail.com',
    description='Package for reading and writing RPN files', requires=['numpy', 'nose'],
    long_description=long_description,
    classifiers=['Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7'],
    keywords="RPN, standard files"
    #package_data={'': ['libpyrmn.so']}
    #ext_modules=[module_wrap]
    # well, it is not ready yet for pgi so the extension should be installed separately
)

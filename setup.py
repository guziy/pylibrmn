from distutils.core import setup
# TODO: get ARMNLIB variable from the environment and compile the rmn_wrapper
import shutil


armnlib = "ARMNLIB"
armnlib_path = ""

native_lib_filename = "libpyrmn.so"

# #Change to the build directory
import os

build_dir = os.path.dirname(os.path.realpath(__file__))

# Add an option to be able to easily disable building of the native part of the library on systems where it is not
# possible ...
build_native_lib = True
BUILD_NATIVE_ENV_VNAME = "BUILD_NATIVE"
if BUILD_NATIVE_ENV_VNAME in os.environ:
    build_native_lib = os.environ[BUILD_NATIVE_ENV_VNAME].lower().strip() in ["true", "1"]
    print("{} = {}".format(BUILD_NATIVE_ENV_VNAME, build_native_lib))


# Build native part of the library
if not os.path.isfile(os.path.join(build_dir, native_lib_filename)) and build_native_lib:
    os.chdir(build_dir)
    print(os.getcwd())

    # build native library using the Makefile
    import subprocess

    subprocess.call(["make"])
    if os.path.isfile(native_lib_filename):
        print("The '{0}' was created. Now you need to add '{1}' to LD_LIBRARY_PATH variable, or put the compiled file "
              "into one of the folders from the list in your current LD_LIBRARY_PATH "
              "".format(native_lib_filename, os.getcwd()))
        print("The list of folders in your current LD_LIBRARY_PATH: ")
        print("--" * 10 + "- Start ----------")
        for fi in os.environ["LD_LIBRARY_PATH"].split(":"):
            print(fi)
        print("--" * 10 + "- End   ----------")

        # copy the library to site-packages
        import distutils.sysconfig

        spack_dir = distutils.sysconfig.get_python_lib()

        try:
            shutil.copyfile(native_lib_filename, os.path.join(
                spack_dir, native_lib_filename
            ))
            print("Copied {} to {}. You will have to remove it manually when uninstalling".format(
                native_lib_filename, spack_dir))
        except IOError as e:
            print("Could not copy {} to {}, will save it in your home directory,"
                  " please, move it to where dynamic libraries are searched".format(
                native_lib_filename, spack_dir, os.path.expanduser("~")))
            shutil.copyfile(native_lib_filename, os.path.join(os.path.expanduser("~"), native_lib_filename))
    else:
        raise Exception("Failed to build '{0}'".format(native_lib_filename))


# raise Exception("ARMNLIB variable is not defined")

# module_wrap = Extension(
# "rpn.libpyrmn",
#    include_dirs=includes,
#    libraries=libraries,
#    library_dirs=library_dirs,
#    sources=["rmn_wrapper.c"])


long_description = """
Requires ssm environment and shared version of the fortran version of rmnlib. Works only on linux..
Written for python 2.7.x and python 3.x.
"""
setup(
    name='pylibrmn',
    version='0.0.32',
    packages=['rpn', 'rpn.util', 'rpn.domains', 'rpn.tests', 'rpn_use_examples'],
    # packages=find_packages("."),
    package_dir={'': 'src'},
    package_data={'rpn.tests': ['data/*', ], },
    license='GPL',
    author='huziy',
    author_email='guziy.sasha@gmail.com',
    description='Package for reading and writing RPN files', requires=['numpy', 'nose'],
    long_description=long_description,
    classifiers=['Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.4', ],
    keywords="RPN, standard files",
    url="https://github.com/guziy/pylibrmn"
    # package_data={'': ['libpyrmn.so']}
    # ext_modules=[module_wrap]
    # well, it is not ready yet for pgi so the extension should be installed separately
)

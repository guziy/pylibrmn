This is a python wrapper around the c/FORTRAN library librmn, which is used for reading RPN files.
The wrapping is done using ctypes python package


Known problems
=========

I haven't figured out yet how to make setup.py use pgi compilers for creating dynamic library....
That is why "pyhon setup.py install" won't work. That is why I am alsosupplying the Makefile in order to help creating the dynamic library.

Install
=======

For the reasons described in "Known problems" section the install procedure is this complicated:

* Create the dynamic library pylibrmn.so and add the path to the containing folder to LD_LIBRARY_PATH environment variable.

    > make
    #put this line to your .profile, so that it is still there after reboot or logout
    > export LD_LIBRARY_PATH=<path to the folder containing pylibrmn.so>:$LD_LIBRARY_PATH

* Add the root of the cloned directory to the PYTHONPATH env. variable


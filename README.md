About
------------
This is a python wrapper around the C/FORTRAN library librmn, which is used for reading RPN files.
The wrapping is done using ctypes python package. The library works with Python 2.7 or later.

Example
=======

The examples moved to the [wiki](https://github.com/guziy/pylibrmn/wiki) of the project.

Requirements
==========
This package is a wrapper around the FORTRAN version of librmn, so it needs this library installed.

* librmn.so (FORTRAN library)
* ctypes (a python package)
* numpy (python package)
* nose (if you want to run tests)


Install
========================

* `pip` can be used to install the package:

```
     pip install pylibrmn
```

It will work provided, you have the FORTRAN version of rmnlib (shared version) and ssm packages needed for compilation and linking of the bridge between FROTRAN and Python.
I use the following commands to prepare my environment:

     . <my_python_env>/bin/activate
     . s.ssmuse.dot fulldev-gcc-46
     . s.ssmuse.dot devtools 
     . s.ssmuse.dot diagtools ###Not necessary for using pylibrmn but used for unit testing

To run the tests in ipython:


    In [1]: cd <path to site-packages folder>/rpn

    In [2]: import nose

    In [5]: nose.run()


<pre>
...................
----------------------------------------------------------------------
Ran 19 tests in 17.800s

OK
</pre>    
 


Contributing
========================================
Any contributions either through bug reports, feature requests or documentation enhancements (e.g. by sending your usage examples) are very welcome. 


Install using `setup.py` and development version of the project from github
========================================

An alternative way to install this module (you might need to have sudo rights to do it in your default python installation or use
virtualenv to create the writable environment. I prefer working with virtualenv and advise you to give it a go, see [this] (https://pypi.python.org/pypi/virtualenv) for more
information):

* Clone this repository using git (or just download .zip archive exported by github):
       
        git  clone  https://github.com/guziy/pylibrmn.git
 
    or if you have a github account you can use ssh link:

        git clone git@github.com:guziy/pylibrmn.git
        

* Install the python wrapper to the site-pacakges directory. `--record` is used so you know which files are copied
   and where (it creates the file files.txt with the list of installed files which you could delete when uninstalling).

        python setup.py install --record files.txt

   It will create `libpyrmn.so` in the current directory.

* Put the compiled library somewhere in your `LD_LIBRARY_PATH`.
     I have put it in the `site-packages/python2.7/` directory, since it is already in my `LD_LIBRARY_PATH`.

* Note: in order to install on guillimin, you have to use `Makefile.guill`, and load ssm package for gfortran beforehand (from the cmmand line).

        . s.ssmuse.dot gfortran-4.6 rmnlib-dev

  To see what else can be used through ssm, do:
        
        s.list_ssm_shortcuts

  To make using the specified make file (`Makefile.guill` in this case) you could do the following:
         
        mv Makefile Makefile.default
        mv Makefile.guill Makefile
        python setup.py install

  *Update:* The same Makefile should work on guillimin and skynet or other system with unified environment installed.

* To test the library you will need `nose` (install using `pip install nose`):

        cd pylibrmn
        nosetests

  You should see something similar in the case of success:

      ............
      ----------------------------------------------------------------------
      Ran 12 tests in 0.881s

      OK 

 

Acknowledgements
=======
Thanks are to the following contributors:
* M. Valin (for help porting to guillimin)
* K. Winger and B. Dugas (for explainations and discussins on the internals of the Fortran version of librmn)
* K. Chikhar (for help with the documentation)


    

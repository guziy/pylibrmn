
About
=========
This is a python wrapper around the C/FORTRAN library librmn, which is used for reading RPN files.
The wrapping is done using ctypes python package

Example
=======

This is an example we've worked through with Kamel. You can find more usage examples [here] (https://github.com/guziy/pylibrmn/tree/master/src/rpn_use_examples).

Import the module and use it.

    In [4]: from rpn.rpn import RPN

    In [5]: r = RPN("mean_TEMP")

`r.g`+TAB gives you the list of methods with names starting with g:

    In [6]: r.g
            r.get_2D_field_on_all_levels                          r.get_current_validity_date                           r.get_longitudes_and_latitudes
            r.get_record_for_name_and_level                    r.get_dateo_of_last_read_record                       r.get_longitudes_and_latitudes_for_the_last_read_rec
            r.get_4d_field                                        r.get_datetime_for_the_last_read_record               r.get_next_record
            r.get_4d_field_fc_hour_as_time                        r.get_first_record_for_name                           r.get_number_of_records
            r.get_all_time_records_for_name                       r.get_first_record_for_name_and_level                 r.get_output_step_in_seconds
            r.get_all_time_records_for_name_and_level             r.get_ip1_from_level                                  r.get_record_for_date_and_level
            r.get_current_info                                    r.get_key_of_any_record                               r.get_records_for_foreacst_hour
            r.get_current_level                                   r.get_list_of_varnames


Or to view all available methods:

    In [46]: dir(r)

To get the list of variable names inside the file:

    In [7]: r.get_list_of_varnames()
    Out[7]:
    array(['>>', 'TT', '^^'],
          dtype='|S2')

We were interested in the mean temperature field (3D) with a single date, to get that field we do:

    In [8]: tt = r.get_4d_field("TT")

Now `tt` is a dictionary

    {time: {level: temperature_2d_field}}

Since we have only one date in the file, the list of levels is retreived as follows:

    In [9]: tt.keys()
    Out[9]: [datetime.datetime(2009, 1, 31, 0, 0)]

    In [10]: tt_3d = tt.items()[0][1]

    In [13]: tt_3d.keys()
    Out[13]:
        [0.10000000149011612,
         0.5,
         3.0,
         900.0,
         5.0,
         1.0,
         10.0,
         15.0,
         400.0,
         20.0,
         150.0,
         925.0,
         30.0,
         800.0,
         550.0,
         300.0,
         50.0,
         950.0,
         700.0,
         650.0,
         450.0,
         70.0,
         200.0,
         975.0,
         850.0,
         600.0,
         350.0,
         100.0,
         1000.0,
         500.0,
         250.0]

Now if you want to get longitudes and latitudes corresponding to the last extracted field, you do this:

    In [28]: lons2d, lats2d = r.get_longitudes_and_latitudes_for_the_last_read_rec()

And voilà you are ready to plot or analyze further your data.


Requirements
==========
This package is a wrapper around the FORTRAN version of librmn, so it needs this library installed.

* librmn.a (FORTRAN library)
* ctypes (a python package)
* numpy (python package)
* nose (if you want to run tests)

Getting the library
=====================



Install
========================

An alternative way to install this module (you might need to have sudo rights to do it in your default python installation or use
virtualenv to create the writable environment. I prefer working with virtualenv and advise you to give it a go, see [this] (https://pypi.python.org/pypi/virtualenv) for more
information):

* Clone this repository using git (or just download .zip archive exported by github):

        git clone git@github.com:guziy/pylibrmn.git

* Install the python wrapper to the site-pacakges directory. `--record` is used so you know which files are copied
   and where (it creates the file files.txt with the list of installed files which you could delete when uninstalling).

        python setup.py install --record files.txt

   It will create `libpyrmn.so` in the current directory.

* Put the compiled library somewhere in your `LD_LIBRARY_PATH`.
     I have put it in the `site-packages/python2.7/` directory, since it is already in my `LD_LIBRARY_PATH`.

* Note: in order to install on guillimin, you have to use `Makefile.guill`, and load ssm package for gfortran beforehand (from the cmmand line).

        . s.ssmuse.dot gfortran-4.6

  To see what else can be used through ssm, do:
        
        s.list_ssm_shortcuts

  To make using the specified make file (`Makefile.guill` in this case) you could do the following:
         
        mv Makefile Makefile.default
        mv Makefile.guill Makefile
        python setup.py install



Acknowledgements
=======
Thanks are to the following contributors:
* M. Valin (for help porting to guillimin)
* K. Winger and B. Dugas (for explainations and discussins on the internals of the Fortran version of librmn)
* K. Chikhar (for help in creating the documentation)


    

This is a python wrapper around the c/FORTRAN library librmn, which is used for reading RPN files.
The wrapping is done using ctypes python package


Known problems
=========

I haven't figured out yet how to make setup.py use pgi compilers for creating dynamic library....
That is why "pyhon setup.py install" won't work. That is why I am also supplying the Makefile in order to help creating the dynamic library.

Requirements
==========
This package is a wrapper around the FORTRAN version of librmn, so it needs this library installed.

* librmn.a (FORTRAN library)
* ctypes (a python package)
* numpy (python package)
* nose (if you want to run tests)



Install
=======

For the reasons described in "Known problems" section the install procedure is this complicated:

* Create the dynamic library `libpyrmn.so` and add the path to the containing folder to `LD_LIBRARY_PATH` environment variable.

        make
  
  put the next line to your `.profile`, so that it is still there after reboot or logout
  
        export LD_LIBRARY_PATH="path to the folder containing libpyrmn.so":$LD_LIBRARY_PATH

* Clone this repository using git through ssh (or just download .zip archive exported by github): 

        git clone git@github.com:guziy/pylibrmn.git

  and add the `pylibrmn/src` from the cloned directory to the `PYTHONPATH` env. variable (i.e. the folder created by the clone command)

* Then fire up ipython and import the `RPN` class as follows:
         
         from rpn.rpn import RPN
         rObj = RPN("path_to_my_rpn_file")

* Note: in order to install on guillimin, you have to use `Makefile.guill`, and load ssm package for gfortran beforehand (from the cmmand line).

        . s.ssmuse.dot gfortran-4.6

  To see what else can be used through ssm, do:
        
        s.list_ssm_shortcuts

  To make using the specified make file do the following:
         
        make -f Makefile.guill

Install using `setup.py`
========================

An alternative way to install this module:
    1. Install the python wrapper to the site-pacakges directory. --record is used so you know which files are copied
       and where (it creates the file files.txt with the list of installed files which you could delete when uninstalling).

        python setup.py install --record files.txt

    2. Compile the libpyrmn.so as discussed in the Install section and put it somewhere in your LD_LIBRARY_PATH.
     I have put it in the site-packages/python2.7/ directory, since it is already in my LD_LIBRARY_PATH.


Example
=======

This is an example we've worked through with Kamel.

    In [5]: r = RPN("mean_TEMP")

`r.g`+TAB gives you the list of methods with names starting with g:
   
    In [6]: r.g
            r.get_2D_field_on_all_levels                          r.get_current_validity_date                           r.get_longitudes_and_latitudes
            r.get_3D_record_for_name_and_level                    r.get_dateo_of_last_read_record                       r.get_longitudes_and_latitudes_for_the_last_read_rec
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

Acknowledgements
=======
Thanks are to the following contributors:
* M. Valin (for help porting to guillimin)
* K. Winger and B. Dugas (for explainations and discussins on the internals of the Fortran version of librmn)
* K. Chikhar (for help in creating the documentation)


    

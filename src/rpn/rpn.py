# The next line is required so the imports work in py2.7 unchanged as in py3.4
from __future__ import absolute_import

from collections import defaultdict, OrderedDict

from rpn import data_types
from ctypes import *
import numpy as np
import os
from rpn import level_kinds
from datetime import datetime
from datetime import timedelta
import copy
import logging
import sys

from rpn.variable import RPNVariable

__author__ = "huziy"
__date__ = "$Apr 5, 2011 12:26:05 PM$"

SUPPORTED_GRID_TYPES = ["Z", "B", "L", "G", "N", "S"]


class RPN(object):
    """
    Class for reading and writing rpn files
    usage:
        rObj = RPN(path = 'your path', mode = 'r')
        rObj = RPN(path = 'your path', mode = 'w')

    methods:
        get_4d_field(self, name="", level_kind=level_kinds.ARBITRARY, label=None)

        get_list_of_varnames(self)

        get_longitudes_and_latitudes_for_the_last_read_rec(self)

        get_first_record_for_name_and_level(self, varname = '', level = -1,
                                                  level_kind = level_kinds.ARBITRARY)

        get_3D_field(self, name = 'SAND', level_kind = level_kinds.ARBITRARY)

        get_current_level(self, level_kind = level_kinds.ARBITRARY)

        get_current_validity_date(self)

        get_first_record_for_name(self, varname)

        get_next_record(self)

        get_longitudes_and_latitudes(self)

        get_key_of_any_record(self)

        get_number_of_records(self)

        suppress_log_messages(self)

        close(self)

        get_ip1_from_level(self, level, level_kind = level_kinds.ARBITRARY)

        write_2D_field(self, name = '', level = 1, level_kind = level_kinds.ARBITRARY, data = None )

        ...

    """
    GRID_TYPE = "grid_type"
    VARNAME_KEY = 'varname'
    handle = None

    log_messages_disabled = False
    n_open_files = 0

    def __init__(self, path='', mode='r', start_century=19, ip_new_style=True, print_log_messages=False,
                 calendar="standard"):
        """
              start_century - is used for the calculation of the origin date, because
              of its ambiguous format MMDDYYR
        """
        if not os.path.isfile(path) and mode == 'r':
            raise Exception('{0} does not exist, or is not a file'.format(path))

        self.path = path
        try:
            self._dll = CDLL('libpyrmn.so', handle=RPN.handle)
        except OSError as err:
            print(err)
            self._dll = CDLL('lib/libpyrmn.so', handle=RPN.handle)

        self.VARNAME_DEFAULT = 5 * ' '
        self.VARTYPE_DEFAULT = 3 * ' '
        self.ETIKET_DEFAULT = 13 * ' '
        self.GRIDTYPE_DEFAULT = 'Z'

        if ip_new_style:
            self.FROM_LEVEL_TO_IP1_MODE = 2
        else:
            self.FROM_LEVEL_TO_IP1_MODE = 1

        self.FROM_IP1_TO_LEVEL_MODE = -1

        self._current_info = None  # map containing info concerning the last read record
        self.start_century = start_century

        self.current_grid_type = self.GRIDTYPE_DEFAULT
        self.current_grid_reference = b'E'

        rpn_file_path = create_string_buffer(path.encode())
        if mode == 'w':
            if os.path.isfile(path):
                os.remove(path)
            options = c_char_p('RND'.encode())
        elif mode == "a":
            options = c_char_p('STD+RND'.encode())
        else:
            options = c_char_p('RND+R/O'.encode())
        dummy = c_int(0)

        self._dll.fnom_wrapper.argtypes = [POINTER(c_int), c_char_p, c_char_p, c_int]
        self._dll.fnom_wrapper.restype = c_int
        self._file_unit = c_int(0)

        fstouv_options = c_char_p("RND".encode()) if mode == "a" else options
        ierr = self._dll.fnom_wrapper(byref(self._file_unit), rpn_file_path, fstouv_options, dummy)

        if ierr != 0:
            raise IOError(
                "Could not associate {} with rpn in-memory object.\n {} files is currently open. ier = {}".format(
                    rpn_file_path.value, RPN.n_open_files, ierr))

        self.nrecords = self._dll.fstouv_wrapper(self._file_unit, options)

        # set argument and return types of the library functions
        # fstinf
        self._dll.fstinf_wrapper.restype = c_int
        self._dll.fstinf_wrapper.argtypes = [c_int, POINTER(c_int), POINTER(c_int), POINTER(c_int),
                                             c_int, c_char_p, c_int, c_int, c_int, c_char_p, c_char_p]

        # ip1_all
        self._dll.ip1_all_wrapper.argtypes = [c_float, c_int]
        self._dll.ip1_all_wrapper.restype = c_int

        # fstluk
        self._dll.fstluk_wrapper.restype = c_int
        self._dll.fstluk_wrapper.argtypes = [POINTER(c_float), c_int, POINTER(c_int), POINTER(c_int), POINTER(c_int)]

        # ezgdef_fmem
        self._dll.ezgdef_fmem_wrapper.restype = c_int
        self._dll.ezgdef_fmem_wrapper.argtypes = [c_int, c_int, c_char_p, c_char_p,
                                                  c_int, c_int, c_int, c_int,
                                                  POINTER(c_float), POINTER(c_float)]
        # gdll
        self._dll.gdll_wrapper.restype = c_int
        self._dll.gdll_wrapper.argtypes = [c_int, POINTER(c_float), POINTER(c_float)]

        # fstfrm
        self._dll.fstfrm_wrapper.restype = c_int
        self._dll.fstfrm_wrapper.argtypes = [c_int]

        # fclos
        self._dll.fclos_wrapper.restype = c_int
        self._dll.fclos_wrapper.argtypes = [c_int]

        # fstsui
        self._dll.fstsui_wrapper.restype = c_int
        self._dll.fstsui_wrapper.argtypes = [c_int, POINTER(c_int), POINTER(c_int), POINTER(c_int)]

        # convip
        p_c_int = POINTER(c_int)
        self._dll.convip_wrapper.argtypes = [p_c_int, POINTER(c_float), p_c_int, p_c_int, c_char_p, p_c_int]

        # fstecr
        self._dll.fstecr_wrapper.argtypes = [
            POINTER(c_float),
            c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int,
            c_int, c_int,
            c_char_p, c_char_p, c_char_p, c_char_p,
            c_int, c_int, c_int, c_int, c_int, c_int
        ]

        # cxgaig
        self._dll.cig_to_xg_wrapper.argtypes = [
            c_char_p,
            POINTER(c_float), POINTER(c_float), POINTER(c_float), POINTER(c_float),
            POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int)
        ]

        # cigaxg
        self._dll.cxg_to_ig_wrapper.argtypes = [
            c_char_p,
            POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int),
            POINTER(c_float), POINTER(c_float), POINTER(c_float), POINTER(c_float),
        ]

        self._dll.fstprm_wrapper.argtypes = [
            c_int,
            POINTER(c_int), POINTER(c_int), POINTER(c_int),
            POINTER(c_int), POINTER(c_int), POINTER(c_int),
            POINTER(c_int), POINTER(c_int),
            POINTER(c_int), POINTER(c_int), POINTER(c_int),
            c_char_p, c_char_p, c_char_p, c_char_p,
            POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int),
            POINTER(c_int), POINTER(c_int),
            POINTER(c_int), POINTER(c_int),
            POINTER(c_int), POINTER(c_int), POINTER(c_int)
        ]

        self._dll.fstprm_wrapper.restype = c_int

        # newdate
        #        *
        #        *AUTHOR   - E. BEAUCHESNE  -  JUN 96
        #        *
        #        *REVISION 001   M. Lepine, B.dugas - automne 2009/janvier 2010 -
        #        *               Ajouter le support des dates etendues (annees 0
        #        *               a 10000) via les nouveaux modes +- 5, 6 et 7.
        #        *REVISION 002   B.dugas - novembre 2010 - Correction au mode -7.
        #        *
        #        *LANGUAGE - fortran
        #        *
        #        *OBJECT(NEWDATE)
        #        *         - CONVERTS A DATE BETWEEN TWO OF THE FOLLOWING FORMATS:
        #        *           PRINTABLE DATE, CMC DATE-TIME STAMP(OLD OR NEW), TRUE DATE
        #        *
        #        *USAGE    - CALL NEWDATE(DAT1,DAT2,DAT3,MODE)
        #        *
        #        *ARGUMENTS
        #        * MODE CAN TAKE THE FOLLOWING VALUES:-7,-6,-5,-4,-3,-2,-1,1,2,3,4,5,6,7
        #        * MODE=1 : STAMP TO (TRUE_DATE AND RUN_NUMBER)
        #        *     OUT - DAT1 - THE TRUEDATE CORRESPONDING TO DAT2
        #        *      IN - DAT2 - CMC DATE-TIME STAMP (OLD OR NEW STYLE)
        #        *     OUT - DAT3 - RUN NUMBER OF THE DATE-TIME STAMP
        #        *      IN - MODE - SET TO 1
        #        * MODE=-1 : (TRUE_DATE AND RUN_NUMBER) TO STAMP
        #        *      IN - DAT1 - TRUEDATE TO BE CONVERTED
        #        *     OUT - DAT2 - CMC DATE-TIME STAMP (OLD OR NEW STYLE)
        #        *      IN - DAT3 - RUN NUMBER OF THE DATE-TIME STAMP
        #        *      IN - MODE - SET TO -1
        #        * MODE=2 : PRINTABLE TO TRUE_DATE
        #        *     OUT - DAT1 - TRUE_DATE
        #        *      IN - DAT2 - DATE OF THE PRINTABLE DATE (YYYYMMDD)
        #        *      IN - DAT3 - TIME OF THE PRINTABLE DATE (HHMMSSHH)
        #        *      IN - MODE - SET TO 2
        #        * MODE=-2 : TRUE_DATE TO PRINTABLE
        #        *      IN - DAT1 - TRUE_DATE
        #        *     OUT - DAT2 - DATE OF THE PRINTABLE DATE (YYYYMMDD)
        #        *     OUT - DAT3 - TIME OF THE PRINTABLE DATE (HHMMSSHH)
        #        *      IN - MODE - SET TO -2
        #        * MODE=3 : PRINTABLE TO STAMP
        #        *     OUT - DAT1 - CMC DATE-TIME STAMP (OLD OR NEW STYLE)
        #        *      IN - DAT2 - DATE OF THE PRINTABLE DATE (YYYYMMDD)
        #        *      IN - DAT3 - TIME OF THE PRINTABLE DATE (HHMMSSHH)
        #        *      IN - MODE - SET TO 3
        #        * MODE=-3 : STAMP TO PRINTABLE
        #        *      IN - DAT1 - CMC DATE-TIME STAMP (OLD OR NEW STYLE)
        #        *     OUT - DAT2 - DATE OF THE PRINTABLE DATE (YYYYMMDD)
        #        *     OUT - DAT3 - TIME OF THE PRINTABLE DATE (HHMMSSHH)
        #        *      IN - MODE - SET TO -3
        #        * MODE=4 : 14 word old style DATE array TO STAMP and array(14)
        #        *     OUT - DAT1 - CMC DATE-TIME STAMP (OLD OR NEW STYLE)
        #        *      IN - DAT2 - 14 word old style DATE array
        #        *      IN - DAT3 - UNUSED
        #        *      IN - MODE - SET TO 4
        #        * MODE=-4 : STAMP TO 14 word old style DATE array
        #        *      IN - DAT1 - CMC DATE-TIME STAMP (OLD OR NEW STYLE)
        #        *     OUT - DAT2 - 14 word old style DATE array
        #        *      IN - DAT3 - UNUSED
        #        *      IN - MODE - SET TO -4
        #        * MODE=5    PRINTABLE TO EXTENDED STAMP (year 0 to 10,000)
        #        *     OUT - DAT1 - EXTENDED DATE-TIME STAMP (NEW STYLE only)
        #        *      IN - DAT2 - DATE OF THE PRINTABLE DATE (YYYYMMDD)
        #        *      IN - DAT3 - TIME OF THE PRINTABLE DATE (HHMMSSHH)
        #        *      IN - MODE - SET TO 5
        #        * MODE=-5   EXTENDED STAMP (year 0 to 10,000) TO PRINTABLE
        #        *      IN - DAT1 - EXTENDED DATE-TIME STAMP (NEW STYLE only)
        #        *     OUT - DAT2 - DATE OF THE PRINTABLE DATE (YYYYMMDD)
        #        *     OUT - DAT3 - TIME OF THE PRINTABLE DATE (HHMMSSHH)
        #        *      IN - MODE - SET TO -5
        #        * MODE=6 :  EXTENDED STAMP TO EXTENDED TRUE_DATE (in hours)
        #        *     OUT - DAT1 - THE TRUEDATE CORRESPONDING TO DAT2
        #        *      IN - DAT2 - CMC DATE-TIME STAMP (OLD OR NEW STYLE)
        #        *     OUT - DAT3 - RUN NUMBER, UNUSED (0)
        #        *      IN - MODE - SET TO 6
        #        * MODE=-6 : EXTENDED TRUE_DATE (in hours) TO EXTENDED STAMP
        #        *      IN - DAT1 - TRUEDATE TO BE CONVERTED
        #        *     OUT - DAT2 - CMC DATE-TIME STAMP (OLD OR NEW STYLE)
        #        *      IN - DAT3 - RUN NUMBER, UNUSED
        #        *      IN - MODE - SET TO -6
        #        * MODE=7  - PRINTABLE TO EXTENDED TRUE_DATE (in hours)
        #        *     OUT - DAT1 - EXTENDED TRUE_DATE
        #        *      IN - DAT2 - DATE OF THE PRINTABLE DATE (YYYYMMDD)
        #        *      IN - DAT3 - TIME OF THE PRINTABLE DATE (HHMMSSHH)
        #        *      IN - MODE - SET TO 7
        #        * MODE=-7 : EXTENDED TRUE_DATE (in hours) TO PRINTABLE
        #        *      IN - DAT1 - EXTENDED TRUE_DATE
        #        *     OUT - DAT2 - DATE OF THE PRINTABLE DATE (YYYYMMDD)
        #        *     OUT - DAT3 - TIME OF THE PRINTABLE DATE (HHMMSSHH)
        #        *      IN - MODE - SET TO -7
        #        *NOTES    - IT IS RECOMMENDED TO ALWAYS USE THIS FUNCTION TO
        #        *           MANIPULATE DATES
        #        *         - IF MODE ISN'T IN THESE VALUES(-7,..,-2,-1,1,2,...,7) OR IF
        #        *           ARGUMENTS AREN'T VALID, NEWDATE HAS A RETURN VALUE OF 1
        #        *         - A TRUE DATE IS AN INTEGER (POSSIBLY NEGATIVE) THAT
        #        *           CONTAINS THE NUMBER OF 5 SECONDS INTERVALS SINCE
        #        *           1980/01/01 00H00. NEGATIVE VALUES ARISE AS
        #        *           THIS CONCEPT APPLIES FROM 1900/01/01.
        #        *         - AN EXTENDED TRUE DATE IS AN INTEGER THAT CONTAINS
        #        *           THE NUMBER OF HOURS SINCE YEAR 00/01/01
        #        *         - SEE INCDATR FOR DETAIL ON CMC DATE-TIME STAMP
        #        *
        #        *         useful constants
        #        *         17280 = nb of 5 sec intervals in a day
        #        *         288   = nb of 5 min intervals in a day
        #        *         jd1900 = julian day for jan 1, 1900       (2415021)
        #        *         jd1980 = julian day for jan 1, 1980       (2444240)
        #        *         jd2236 = julian day for jan 1, 2236       (2537742)
        #        *         jd0    = julian day for jan 1, 0          (1721060)
        #        *         jd10k  = julian day for jan 1, 10,000     (5373485)
        #        *         td1900 = truedate  for  jan 1, 1900 , 00Z (-504904320)
        #        *         td2000 = truedate  for  jan 1, 2000 , 00Z (+126230400)
        #        *         tdstart = base for newdates ( jan 1, 1980, 00Z)
        #        *         max_offset = (((jd10k-jd0)*24)/8)*10      (109572750)
        #        *         exception = extended truedate for jan 1, 1901, 01Z
        #        *         troisg = 3 000 000 000
        #        *WARNING  - IF NEWDATE RETURNS 1, OUTPUTS CAN TAKE ANY VALUE
        #        *

        self._dll.newdate_wrapper.argtypes = [
            POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int)
        ]

        self._dateo_format = "%Y%m%d%H%M%S"

        # fstopc
        self._dll.fstopc_wrapper.argtypes = [
            c_char_p, c_char_p, c_int
        ]

        self._dll.fstopc_wrapper.restype = c_int

        # fstlnk
        self._dll.fstlnk_wrapper.argtypes = [POINTER(c_int), POINTER(c_int)]
        self._dll.fstlnk_wrapper.restype = c_int

        # fstunl
        self._dll.fstunl_wrapper.argtypes = [p_c_int, p_c_int]
        self._dll.fstunl_wrapper.restype = c_int

        # Disable log messages
        if not self.log_messages_disabled and not print_log_messages:
            self.suppress_log_messages()
            self.log_messages_disabled = True

        RPN.n_open_files += 1  # track number of open files

        # possible values: standard, 365_day, 360_day
        self.calendar = calendar

        self._variables = None



    @property
    def variables(self):
        if self._variables is None:
            # initialize the dict of RPNVariable objects

            self._variables = OrderedDict()

            for vname in self.get_list_of_varnames():
                if vname in [">>", "^^", "HY", "!!"]:
                    continue

                self._variables[vname] = RPNVariable(self, vname)

        return self._variables

    @property
    def file_unit(self):
        return self._file_unit.value

    @file_unit.setter
    def file_unit(self, value):
        raise AttributeError("File unit cannot be set")

    def _dateo_to_string(self, dateo_int):
        """
        return dateo as string
        """
        res_date = c_int()
        res_time = c_int()
        mode = c_int(-3)
        self._dll.newdate_wrapper(byref(c_int(dateo_int)), byref(res_date), byref(res_time), byref(mode))

        s_date = "{0:08d}{1:08d}".format(res_date.value, res_time.value)
        return s_date[:-2]

    def _string_to_dateo(self, dateo_str):
        """
        return dateo as int code
        """
        mode = c_int(3)
        date = datetime.strptime(dateo_str, self._dateo_format)
        res_date = c_int(int(date.strftime("%Y%m%d")))
        res_time = c_int(int(date.strftime("%H%M%S%H")))
        dateo_int = c_int()
        self._dll.newdate_wrapper(byref(dateo_int), byref(res_date), byref(res_time), byref(mode))
        return dateo_int.value

    def get_record_for_date_and_level(self, var_name="", date=None, date_o=None, level=-1,
                                      level_kind=level_kinds.ARBITRARY):
        """

        """

        if date_o is None:
            raise Exception("You have to specify origin date, usually it is a start date of your simulation")

        dt = date - date_o

        forecast_hour = int(dt.total_seconds() / 3600.0)

        ip1 = c_int(-1)
        ip2 = c_int(forecast_hour)
        ip3 = c_int(-1)

        if level > -1:
            ip1 = c_int(self._dll.ip1_all_wrapper(c_float(level), c_int(level_kind)))

        ni = c_int(-1)
        nj = c_int(-1)
        nk = c_int(-1)

        etiket = create_string_buffer(self.ETIKET_DEFAULT.encode())
        in_typvar = create_string_buffer(self.VARTYPE_DEFAULT.encode())

        in_nomvar = create_string_buffer(var_name.encode())

        key = self._dll.fstinf_wrapper(self._file_unit, byref(ni), byref(nj), byref(nk), c_int(-1), etiket,
                                       ip1, ip2, ip3, in_typvar, in_nomvar)

        if key < 0:
            return None
        else:
            return self._get_data_by_key(key)

    def get_records_for_foreacst_hour(self, var_name="", forecast_hour=None, level_kind=level_kinds.ARBITRARY):
        """
        datev - forecast hour starting from the simulation start
        :param var_name:  name of the variable in the rpn file
        :param forecast_hour:
        :param level_kind:
        #TODO: make sure it works, read on datev and ip2 parameters
        """
        ip1 = c_int(-1)
        ip2 = c_int(forecast_hour)
        ip3 = c_int(-1)

        ni = c_int(-1)
        nj = c_int(-1)
        nk = c_int(-1)

        etiket = create_string_buffer(self.ETIKET_DEFAULT.encode())
        in_typvar = create_string_buffer(self.VARTYPE_DEFAULT.encode())
        in_nomvar = create_string_buffer(var_name.encode())
        res = {}
        key = self._dll.fstinf_wrapper(self._file_unit, byref(ni), byref(nj), byref(nk), c_int(-1), etiket,
                                       ip1, ip2, ip3, in_typvar, in_nomvar)

        while key >= 0:
            data = self._get_data_by_key(key)
            lev = self.get_current_level()

            if lev in res.keys():
                msg = "WARNING: this file contains more than one field {0} for the level {1}, " \
                      "reading only the first one".format(var_name, lev)
                print(msg)
                break

            res[lev] = data
            key = self._dll.fstsui_wrapper(self._file_unit, byref(ni), byref(nj), byref(nk))
        return res

    def get_output_step_in_seconds(self):
        raise NotImplementedError("Not yet implemented")

    def get_list_of_varnames(self):
        """
        :returns a list of variable names inside the file
        """
        ip1 = c_int(-1)
        ip2 = c_int(-1)
        ip3 = c_int(-1)

        ni = c_int(-1)
        nj = c_int(-1)
        nk = c_int(-1)

        etiket = create_string_buffer(self.ETIKET_DEFAULT.encode())
        in_typvar = create_string_buffer(self.VARTYPE_DEFAULT.encode())
        in_nomvar = create_string_buffer(self.VARNAME_DEFAULT.encode())
        key = self._dll.fstinf_wrapper(self._file_unit, byref(ni), byref(nj), byref(nk), c_int(-1), etiket,
                                       ip1, ip2, ip3, in_typvar, in_nomvar)

        names = []
        while key >= 0:
            # data = self._get_data_by_key(key)
            # lev = self.get_current_level(level_kind=level_kind)
            # res[lev] = data
            names.append(self._get_record_info(key)[self.VARNAME_KEY])
            key = self._dll.fstsui_wrapper(self._file_unit, byref(ni), byref(nj), byref(nk))

        return np.unique(names)

    def suppress_log_messages(self):
        self._dll.fstopc_wrapper("MSGLVL".encode(), "SYSTEM".encode(), 0)

    def close(self):
        """
        Close the file connection and cleanup
        """

        self._dll.fstfrm_wrapper(self._file_unit)
        self._dll.fclos_wrapper(self._file_unit)
        self._file_unit = c_int(-99999)
        RPN.n_open_files -= 1

    def get_number_of_records(self):
        """
        returns number of records inside the rpn file
        """
        return self.nrecords

    def get_key_of_any_record(self):
        """
        Returns the key of the first data record
        """
        ni = c_int(0)
        nj = c_int(0)
        nk = c_int(0)
        datev = c_int(-1)
        etiket = create_string_buffer(self.ETIKET_DEFAULT.encode())

        ip1 = c_int(-1)
        ip2 = c_int(-1)
        ip3 = c_int(-1)
        in_typvar = create_string_buffer(self.VARTYPE_DEFAULT.encode())

        in_nomvar = create_string_buffer(self.VARNAME_DEFAULT.encode())

        # int fstinf_wrapper(int iun, int *ni, int *nj, int *nk, int datev,char *in_etiket,
        # int ip1, int ip2, int ip3, char *in_typvar, char *in_nomvar)

        key = self._dll.fstinf_wrapper(self._file_unit, byref(ni), byref(nj), byref(nk), datev, etiket,
                                       ip1, ip2, ip3, in_typvar, in_nomvar)

        if key < 0:
            raise Exception("key value is not valid {0}".format(key))

        return key

    def get_record_key_for_name_and_level(self, varname='', level=-1,
                                          level_kind=level_kinds.ARBITRARY, label=None):

        """
        Search and return a key for a 2d field inside of the RPN file for a given <param>vaname</param> and <param>level</param>
        If there are many such records in the rpn file (i.e. for different time steps), then the first one is returned
        Possible `level_kind` values are listed in rpn.level_kinds module
        """

        ni = c_int(0)
        nj = c_int(0)
        nk = c_int(0)
        datev = c_int(-1)

        if label is None:
            etiket = create_string_buffer(self.ETIKET_DEFAULT.encode())
        else:
            etiket = create_string_buffer(label.encode() if hasattr(label, "encode") else label)

        if level == -1:
            ip1 = c_int(-1)
        else:
            ip1 = c_int(self._dll.ip1_all_wrapper(c_float(level), c_int(level_kind)))
        ip2 = c_int(-1)
        ip3 = c_int(-1)
        in_typvar = create_string_buffer(self.VARTYPE_DEFAULT.encode())

        in_nomvar = self.VARNAME_DEFAULT
        in_nomvar = varname + in_nomvar
        in_nomvar = in_nomvar[:8]
        in_nomvar = create_string_buffer(in_nomvar.encode())

        # int fstinf_wrapper(int iun, int *ni, int *nj, int *nk, int datev,char *in_etiket,
        # int ip1, int ip2, int ip3, char *in_typvar, char *in_nomvar)

        key = self._dll.fstinf_wrapper(self._file_unit, byref(ni), byref(nj), byref(nk), datev, etiket,
                                       ip1, ip2, ip3, in_typvar, in_nomvar)

        # print in_typvar.value
        # print("key({0}) = {1}".format(in_nomvar.value, key))

        if key < 0:
            raise Exception(
                "varname = {0}, at level {1} is not found  in {2}.".format(varname, level, self.path))

        return key


    def get_field_shape(self, varname=""):
        """
        get the shape of a field inside of the rpn file without reading the field into memory
        (ni, nj) corresponding to the (longitude, latitude) dimensions, respectively
        :param key:
        """
        key = self.get_record_key_for_name_and_level(varname=varname)
        return tuple([s.value for s in self._get_record_info(key=key, update_current_info=False)["shape"][:2]])



    def get_date_level_key_mapping_for_name(self, varname=""):
        """
        Get the mapping of date: {level: key} for the varname, that should be used for lazy loading of the data
        :param varname:
        """
        ip1 = c_int(-1)
        ip2 = c_int(-1)
        ip3 = c_int(-1)

        ni = c_int(-1)
        nj = c_int(-1)
        nk = c_int(-1)

        etiket = create_string_buffer(self.ETIKET_DEFAULT.encode())
        in_typvar = create_string_buffer(self.VARTYPE_DEFAULT.encode())
        in_nomvar = create_string_buffer(varname.encode())
        key = self._dll.fstinf_wrapper(self._file_unit, byref(ni), byref(nj), byref(nk), c_int(-1), etiket,
                                       ip1, ip2, ip3, in_typvar, in_nomvar)

        result = defaultdict(dict)
        while key >= 0:
            # data = self._get_data_by_key(key)
            # lev = self.get_current_level(level_kind=level_kind)
            # res[lev] = data


            # read info corresponding to the key from the standard file
            info = self._get_record_info(key)

            # get the date for the key

            # previously was coded like this, but it is not general enough
            # forecast_hour = info["ip"][1].value
            forecast_hour = info["dt_seconds"].value * info["npas"].value / 3600

            from netcdftime import utime

            cdf_time = utime("hours since {:%Y-%m-%d %H:%M:%S}".format(self._current_info["dateo"]),
                             calendar=self.calendar)

            try:
                d = cdf_time.num2date(forecast_hour)
            except ValueError as verr:
                print(info)
                raise verr

            # get the level
            ip1 = info["ip"][0].value

            level = self.ip1_to_real_val(ip1)

            result[d][level] = key

            # get the next key for the variable
            key = self._dll.fstsui_wrapper(self._file_unit, byref(ni), byref(nj), byref(nk))

        return result

    def get_record_for_name_and_level(self, varname='', level=-1,
                                      level_kind=level_kinds.ARBITRARY, label=None):
        """
        Search and return 2d field for a given <param>vaname</param> and <param>level</param>
        If there are many such records in the rpn file (i.e. for different time steps), then the first one is returned
        Possible `level_kind` values are listed in rpn.level_kinds module
        """
        key = self.get_record_key_for_name_and_level(varname=varname, level=level, level_kind=level_kind, label=label)
        return self._get_data_by_key(key).squeeze()

    def _get_data_by_key(self, record_key):
        """
        Get data record corresponding to the record_key
        :type record_key: c_int
        """
        self._get_record_info(record_key)

        # print self._current_info[self.VARNAME_KEY].value
        the_type = self._get_current_data_type()
        # print the_type
        ni, nj, nk = self._current_info["shape"]
        data = np.zeros((nk.value * nj.value * ni.value,), dtype=the_type)

        # read the record
        self._dll.fstluk_wrapper(data.ctypes.data_as(POINTER(c_float)), record_key, ni, nj, nk)

        data = np.reshape(data, (ni.value, nj.value, nk.value), order='F')
        return data

    def get_proj_parameters_for_the_last_read_rec(self):
        """
        :return grid type and grid parameters in a dictionary
        """
        if self._current_info is None:
            raise Exception("No records has been read yet, or its metadata has not yet been saved.")

        data_ips = self._current_info["ip"]
        data_ig = self._current_info['ig']

        datev = c_int(-1)

        result = {}

        x1 = c_float(-1)
        x2 = c_float(-1)
        x3 = c_float(-1)
        x4 = c_float(-1)

        # find out info about the coordinates for the last read record
        in_nomvar = create_string_buffer(">>".encode())
        in_typvar = create_string_buffer(self.VARTYPE_DEFAULT.encode())

        ni, nj, nk = [c_int(-1) for _ in range(3)]
        etiket = create_string_buffer(self.ETIKET_DEFAULT.encode())

        # ips for the coordinate record
        ip1, ip2, ip3 = data_ig[:3]

        key = self._dll.fstinf_wrapper(self._file_unit, byref(ni), byref(nj), byref(nk), datev, etiket,
                                       ip1, ip2, ip3, in_typvar, in_nomvar)

        # _current_info field usually contains the metadata for the last read data record
        # since this one is a coordinate record, do not update the value of the current_info field
        info = self._get_record_info(key, update_current_info=False)
        coord_ig = info["ig"]

        grid_type = info["grid_type"]
        self._dll.cig_to_xg_wrapper(grid_type,
                                    byref(x1), byref(x2), byref(x3), byref(x4),
                                    coord_ig[0], coord_ig[1], coord_ig[2], coord_ig[3])

        grid_type = grid_type.value.decode()
        result["grid_type"] = grid_type
        if grid_type == "L":  # real lat lon grid
            result["ll_lat"] = x1.value
            result["ll_lon"] = x2.value
            result["dlat"] = x3.value
            result["dlon"] = x4.value
        elif grid_type == "E":
            result["lat1"] = x1.value
            result["lon1"] = x2.value
            result["lat2"] = x3.value
            result["lon2"] = x4.value

        return result

    def get_tictacs_for_the_last_read_record(self):
        """ Returns 1D arrays in rotated lat/lon coordinates"""

        if self._current_info is None:
            raise Exception("No records has been read yet, or its metadata has not yet been saved.")

        if self._current_info[self.VARNAME_KEY] in [">>", "^^"]:
            raise Exception("Trying to get coordinates for coordinate records, this operation is only "
                            "possible for data records. Please read in some data field first")

        # Make sure the internal info is not modified by the extraction of coordinates
        _info_backup = copy.deepcopy(self._current_info)

        ig = self._current_info['ig']

        ni = c_int(0)
        nj = c_int(0)
        nk = c_int(0)
        datev = c_int(-1)
        etiket = create_string_buffer(self.ETIKET_DEFAULT.encode())

        # print ig
        ip1, ip2, ip3 = ig[:3]
        in_typvar = create_string_buffer(self.VARTYPE_DEFAULT.encode())

        in_nomvar = create_string_buffer(">>".encode())

        key_hor = self._dll.fstinf_wrapper(self._file_unit, byref(ni), byref(nj), byref(nk), datev, etiket,
                                           ip1, ip2, ip3, in_typvar, in_nomvar)

        in_nomvar = create_string_buffer("^^".encode())
        key_ver = self._dll.fstinf_wrapper(self._file_unit, byref(ni), byref(nj), byref(nk), datev, etiket,
                                           ip1, ip2, ip3, in_typvar, in_nomvar)

        if key_hor < 0 or key_ver < 0:
            raise Exception("key value is not valid {0}".format(min(key_hor, key_ver)))

        rlons = self._get_data_by_key(key_hor).squeeze()
        rlats = self._get_data_by_key(key_ver).squeeze()

        self._current_info = _info_backup

        return rlons, rlats

    def get_longitudes_and_latitudes_for_the_last_read_rec(self):
        """
        Note: should not be called within a loop using get_next_record, because it'll mess up the search query for the records
        finds georeference
        """
        if self._current_info is None:
            raise Exception("No records has been read yet, or its metadata has not yet been saved.")

        if self._current_info[self.VARNAME_KEY] in [">>", "^^"]:
            raise Exception("Trying to get coordinates for coordinate records, this operation is only "
                            "possible for data records. Please read in some data field first")

        # Make sure the internal info is not modified by the extraction of coordinates
        _info_backup = copy.deepcopy(self._current_info)

        ig = self._current_info['ig']

        current_info = self.get_current_info()

        grid_type = current_info["grid_type"]
        ni, nj, nk = current_info["shape"]

        if grid_type.strip().upper() not in SUPPORTED_GRID_TYPES:
            raise NotImplementedError("unknown grid type {}".format(grid_type.strip().upper()))

        # B grid type
        if grid_type.strip().upper() == "B":
            lon_min = 0.0
            dlon = 360.0 / float(ni - 1)
            if ig[0].value == 0:
                dlat = 180.0 / float(nj - 1)
            else:
                dlat = 90.0 / float(nj - 1)

            lons = [lon_min + dlon * i for i in range(ni)]
            # lons[-1] = lon_min + 360
            if ig[1].value == 0:  # South -> North (pt (1,1) is at the bottom of the grid)
                if ig[0].value == 1:
                    lat_min = 0.0
                else:
                    lat_min = -90.0

                lats = [lat_min + dlat * i for i in range(nj)]
                lats2d, lons2d = np.meshgrid(lats, lons)

            else:  # North -> South (pt (1,1) is at the top of the grid)
                if ig[0].value == 2:
                    lat_max = 0.0
                else:
                    lat_max = 90.0

                lats = [lat_max - i * dlat for i in range(nj)]
                lats2d, lons2d = np.meshgrid(lats, lons)
            return lons2d, lats2d

        # L  grid type
        if grid_type.strip().upper() == "L":
            ll_lat = c_float(-1)
            ll_lon = c_float(-1)
            dlon = c_float(-1)
            dlat = c_float(-1)
            self._dll.cig_to_xg_wrapper(create_string_buffer(grid_type.encode()),
                                        byref(ll_lat), byref(ll_lon), byref(dlat), byref(dlon),
                                        ig[0], ig[1], ig[2], ig[3])

            ll_latv = ll_lat.value
            ll_lonv = ll_lon.value
            dlonv = dlon.value
            dlatv = dlat.value

            lons1d = dlonv * np.arange(ni) + ll_lonv
            lats1d = dlatv * np.arange(nj) + ll_latv

            lats2d, lons2d = np.meshgrid(lats1d, lons1d)
            return lons2d, lats2d

        if grid_type.strip().upper() == "G":
            lon_min = 0.0
            dlon = 360.0 / float(ni)

            lons = [lon_min + dlon * i for i in range(ni)]

            from rpn.domains import gauss_grid
            lats = gauss_grid.gaussian_latitudes(nj)[0]
            if ig[0].value == 1:  # Northen hemisphere
                lats = lats[nj:]
            elif ig[0].value == 2:  # Southern hemisphere
                lats = lats[:nj]
            else:  # global
                lats = gauss_grid.gaussian_latitudes(nj // 2)[0]

            if ig[1].value == 0:  # South -> North (pt (1,1) is at the bottom of the grid)
                pass
            else:  # North -> South (pt (1,1) is at the top of the grid)
                lats = reversed(lats)

            lats2d, lons2d = np.meshgrid(lats, lons)
            return lons2d, lats2d

        if grid_type.strip().upper() in ["N", "S"]:
            from rpn.util import polar_stereographic as ps

            pole_i = c_float(-1)
            pole_j = c_float(-1)
            d60 = c_float(-1)
            dgrw = c_float(-1)
            self._dll.cig_to_xg_wrapper(create_string_buffer(grid_type.encode()),
                                        byref(pole_i), byref(pole_j), byref(d60), byref(dgrw),
                                        ig[0], ig[1], ig[2], ig[3])

            if grid_type.strip().upper() == "N":
                hem = ps.NORTHERN_HEM
            else:
                hem = ps.SOUTHERN_HEM
            return ps.get_longitudes_and_latitudes_2d_for_ps_grid(pole_i.value,
                                                                  pole_j.value,
                                                                  d60.value,
                                                                  dgrw.value, ni, nj,
                                                                  hemisphere=hem)

        ni = c_int(0)
        nj = c_int(0)
        nk = c_int(0)
        datev = c_int(-1)
        etiket = create_string_buffer(self.ETIKET_DEFAULT.encode())

        # print ig
        ip1, ip2, ip3 = ig[:3]
        in_typvar = create_string_buffer(self.VARTYPE_DEFAULT.encode())

        in_nomvar = create_string_buffer(">>".encode())

        key_hor = self._dll.fstinf_wrapper(self._file_unit, byref(ni), byref(nj), byref(nk), datev, etiket,
                                           ip1, ip2, ip3, in_typvar, in_nomvar)

        in_nomvar = create_string_buffer("^^".encode())
        key_ver = self._dll.fstinf_wrapper(self._file_unit, byref(ni), byref(nj), byref(nk), datev, etiket,
                                           ip1, ip2, ip3, in_typvar, in_nomvar)

        if key_hor < 0 or key_ver < 0:
            raise Exception("key value is not valid {0}".format(min(key_hor, key_ver)))

        lons = self._get_data_by_key(key_hor).squeeze()
        lats = self._get_data_by_key(key_ver).squeeze()

        ig = self._current_info["ig"]
        n_lons = lons.shape[0]
        n_lats = lats.shape[0]

        grid_type = self._current_info[RPN.GRID_TYPE]
        data_grid_type = c_char_p("Z".encode())

        ezgdef = self._dll.ezgdef_fmem_wrapper(c_int(n_lons), c_int(n_lats),
                                               data_grid_type, grid_type,
                                               ig[0], ig[1], ig[2], ig[3],
                                               lons.ctypes.data_as(POINTER(c_float)),
                                               lats.ctypes.data_as(POINTER(c_float)))

        the_type = self._get_current_data_type()
        lons_2d = np.zeros((n_lats, n_lons), dtype=the_type)
        lats_2d = np.zeros((n_lats, n_lons), dtype=the_type)

        self._dll.gdll_wrapper(ezgdef, lats_2d.ctypes.data_as(POINTER(c_float)),
                               lons_2d.ctypes.data_as(POINTER(c_float)))

        self._current_info = _info_backup

        # print "lon params = ", lons_2d.shape, np.min(lons_2d), np.max(lons_2d)
        return np.transpose(lons_2d).copy(), np.transpose(lats_2d).copy()

    # get longitudes for the record
    def get_longitudes_and_latitudes(self):
        """
        get longitudes and latitudes of the fields in the rpn file,

        An rpn file can contain several
        """

        sys.stderr.write("Warning this function is deprecated, it works only for Z grid types \n"
                         "Please use RPN.get_longitudes_and_latitudes_for_the_last_read_rec()\n")

        key = self.get_key_of_any_record()
        info = self._get_record_info(key, verbose=True)  # sets grid type
        ig = info['ig']

        ni = c_int(0)
        nj = c_int(0)
        nk = c_int(0)
        datev = c_int(-1)

        ip1 = c_int(-1)
        ip2 = c_int(-1)
        ip3 = c_int(-1)

        # read longitudes
        in_nomvar = '>>'
        in_nomvar = create_string_buffer(in_nomvar[:2])
        etiket = create_string_buffer(' ')
        in_typvar = create_string_buffer(' ')

        hor_key = self._dll.fstinf_wrapper(self._file_unit, byref(ni), byref(nj), byref(nk),
                                           datev, etiket, ip1, ip2, ip3, in_typvar, in_nomvar)
        # print in_nomvar.value
        # print in_typvar.value
        assert hor_key >= 0, 'hor_key = {0}'.format(hor_key)

        # print 'hor_key = ', hor_key

        lons = self._get_data_by_key(hor_key)[:, 0, 0]

        # read latitudes
        in_nomvar = '^^'
        in_nomvar = create_string_buffer(in_nomvar[:2])
        ver_key = self._dll.fstinf_wrapper(self._file_unit, byref(ni), byref(nj), byref(nk),
                                           datev, etiket, ip1, ip2, ip3, in_typvar, in_nomvar)

        lats = self._get_data_by_key(ver_key)[0, :, 0]

        ig = self._current_info["ig"]
        n_lons = lons.shape[0]
        n_lats = lats.shape[0]

        # print 'grid type: ', self.current_grid_type
        # print 'grid ref: ', self.current_grid_reference


        # print 'grid type: ',  self.current_grid_type
        grid_type = create_string_buffer("Z")  # create_string_buffer(self.current_grid_type)
        grid_reference = create_string_buffer(self.current_grid_reference)

        ezgdef = self._dll.ezgdef_fmem_wrapper(c_int(n_lons), c_int(n_lats),
                                               grid_type, grid_reference,
                                               ig[0], ig[1], ig[2], ig[3],
                                               lons.ctypes.data_as(POINTER(c_float)),
                                               lats.ctypes.data_as(POINTER(c_float)))

        the_type = self._get_current_data_type()
        lons_2d = np.zeros((n_lats, n_lons), dtype=the_type)
        lats_2d = np.zeros((n_lats, n_lons), dtype=the_type)

        self._dll.gdll_wrapper(ezgdef, lats_2d.ctypes.data_as(POINTER(c_float)),
                               lons_2d.ctypes.data_as(POINTER(c_float)))

        return np.transpose(lons_2d), np.transpose(lats_2d)

    def reset_current_info(self):
        self._current_info = None

    def get_first_record_for_name(self, varname, label=None):
        """
        returns first met record for the field varname
        """
        return self.get_first_record_for_name_and_level(varname, -1, label=label)

    def get_first_record_for_name_and_level(self, varname='', level=-1,
                                            level_kind=level_kinds.ARBITRARY, label=None):
        """
        returns data of the first encountered record that satisfies the
        query, and returns the 2d field, if the rcord is 3d then it takes the 2d subset
        corresponding to the first 3rd dimension
        """
        return self.get_record_for_name_and_level(varname=varname, level=level,
                                                  level_kind=level_kind, label=label)

    def _get_record_info(self, key, verbose=False, update_current_info=True):
        """
        store the properties of the record with key, to the internal dictionary
        """
        dateo = c_int()
        dt_seconds = c_int()
        npas = c_int()
        ni = c_int()
        nj = c_int()
        nk = c_int()

        nbits = c_int()
        datyp = c_int()

        ip1 = c_int()
        ip2 = c_int()
        ip3 = c_int()

        typvar = create_string_buffer(self.VARTYPE_DEFAULT.encode())
        nomvar = create_string_buffer(self.VARNAME_DEFAULT.encode())
        etiket = create_string_buffer(self.ETIKET_DEFAULT.encode())
        grid_type = create_string_buffer(self.GRIDTYPE_DEFAULT.encode())

        ig1 = c_int()
        ig2 = c_int()
        ig3 = c_int()
        ig4 = c_int()

        extra1 = c_int()
        extra2 = c_int()
        extra3 = c_int()

        swa = c_int()
        lng = c_int()
        dltf = c_int()
        ubc = c_int()

        self._dll.fstprm_wrapper(c_int(key),
                                 byref(dateo), byref(dt_seconds), byref(npas),
                                 byref(ni), byref(nj), byref(nk),
                                 byref(nbits), byref(datyp),
                                 byref(ip1), byref(ip2), byref(ip3),

                                 typvar, nomvar, etiket, grid_type,
                                 byref(ig1), byref(ig2), byref(ig3), byref(ig4),
                                 byref(swa), byref(lng),
                                 byref(dltf), byref(ubc),
                                 byref(extra1), byref(extra2), byref(extra3))

        if verbose:
            print('ip ', [ip1.value, ip2.value, ip3.value])
            print('grtype', grid_type.value)
            print('ig', [ig1.value, ig2.value, ig3.value, ig4.value])
            print('varname: ', nomvar.value)

        if '>>'.encode() in nomvar.value or '^^'.encode() in nomvar.value:
            self.current_grid_reference = grid_type.value
        else:
            self.current_grid_type = grid_type.value
            # print 'current grid type ', self.current_grid_type

        try:
            dateo_s = self._dateo_to_string(dateo.value)
            the_dateo = datetime.strptime(dateo_s, self._dateo_format)
        except ValueError:
            try:
                dateo_s = self._dateo_to_string(extra1.value)
                the_dateo = datetime.strptime(dateo_s, self._dateo_format)
            except Exception as e1:
                # print(e1)
                # print(dateo.value)
                dateo_s = "{0}010101000000".format(self.start_century)
                sys.stderr.write(
                    "dateo is not set for {}, using default:{}\n".format(nomvar.value.decode().strip(), dateo_s))
                the_dateo = datetime.strptime(dateo_s, self._dateo_format)

        # if the_dateo.year // 100 != self.start_century:
        # year = self.start_century * 100 + the_dateo.year % 100
        # the_dateo = datetime( year, the_dateo.month, the_dateo.day, the_dateo.hour, the_dateo.minute)

        result = {'ig': [ig1, ig2, ig3, ig4],
                  'ip': [ip1, ip2, ip3],
                  'shape': [ni, nj, nk],
                  'dateo': the_dateo,
                  'dt_seconds': dt_seconds,
                  'npas': npas,
                  'varname': nomvar.value.decode().strip(),
                  "var_type": typvar,
                  "data_type": datyp,
                  "nbits": nbits,
                  "grid_type": grid_type,
                  "dateo_rpn_format": dateo,
                  "extra1": extra1,
                  "label": etiket.value}

        if update_current_info:
            self._current_info = result  # update info from the last read record

        # self._set_origin_date(date_o=the_dateo)
        return result

    def _get_current_data_type(self):
        # determine data type of the data inside the
        data_type = self._current_info["data_type"].value
        nbits = self._current_info["nbits"].value
        if nbits == 32:
            if data_type in [data_types.IEEE_floating_point, data_types.compressed_IEEE, data_types.floating_point,
                             data_types.masked_floating_point]:
                return np.float32
            elif data_type == data_types.signed_integer:
                # print "data_type = ", data_type
                return np.int32
            else:
                sys.stderr.write(
                    "The datatype for >>{}<< is not recognized, using float32\n".format(self._current_info["varname"]))
                return np.float32

        elif nbits == 64:
            return np.float64
        elif nbits == 16 or nbits == 24:
            if data_type in [data_types.compressed_floating_point, data_types.floating_point,
                             data_types.floating_point_16_bit, data_types.IEEE_floating_point,
                             data_types.compressed_IEEE]:
                return np.float32
            return np.float16
        elif nbits == 8:
            if data_type in [data_types.unsigned_integer]:
                return np.uint32
            else:
                sys.stderr.write(
                    "The datatype is >>{}<< and >>{}<< bits \n".format(data_type, nbits))
        else:
            raise Exception("nbits is: {0}".format(nbits))

    def get_next_record(self):
        """
        returns None, if there is no next record satisfying the last search parameters

        Note: if there were previous queries to the file then it will look for the next record satisfying the query
        """
        if self._current_info is None:
            key = self.get_key_of_any_record()
            self._get_record_info(key)
            return self._get_data_by_key(key)[:, :, 0]

        [ni, nj, nk] = self._current_info['shape']
        key = self._dll.fstsui_wrapper(self._file_unit, byref(ni), byref(nj), byref(nk))

        if key <= 0:
            return None

        return self._get_data_by_key(key)[:, :, 0]

    def get_current_level(self):
        """
        returns level value for the last read record
        """
        ip1 = self._current_info['ip'][0]
        return self.ip1_to_real_val(ip1.value)

    def ip1_to_real_val(self, ip1=0):
        """
        Note: level_kind is determined from ip1
        :param ip1:
        :return:
        """

        ip1_ = c_int(ip1)
        string = create_string_buffer(' '.encode(), 128)
        level_value = c_float(-1)

        kind = c_int(-1)
        mode = c_int(-1)
        flag = c_int(0)

        # print 'before convip'
        self._dll.convip_wrapper(byref(ip1_), byref(level_value), byref(kind), byref(mode), string, byref(flag))

        return level_value.value

    def get_current_validity_date(self):
        """
        returns validity date in hours from the simulation start, of the last read record
        return None if no data has been read yet
        """
        if self._current_info is None:
            return None

        return self._current_info['ip'][1].value  # ip2

    def get_dateo_of_last_read_record(self):
        """
        returns date of origin, the start date of the simulation
        """
        if self._current_info:
            return self._current_info["dateo"]
        else:
            raise Exception("No current info has been stored: please make sure you read some records first.")

    def get_cdf_datetime_for_the_last_read_record(self):
        """
        use netcdftime, which supports different calendar types
        :return:
        """
        if self._current_info is not None:
            try:

                # extra can contain the validity date
                extra1 = self._current_info["extra1"].value
                if extra1 > 0:
                    date_s = self._dateo_to_string(extra1)
                    return datetime.strptime(date_s, self._dateo_format)

                forecast_hour = self.get_current_validity_date()
                assert forecast_hour >= 0

                if not hasattr(self, "dateo_fallback"):
                    self.dateo_fallback = self._current_info["dateo"]

                from netcdftime import utime

                cdf_time = utime("hours since {:%Y-%m-%d %H:%M:%S}".format(self._current_info["dateo"]),
                                 calendar=self.calendar)

                d = cdf_time.num2date(forecast_hour)
                print(d, forecast_hour, self._current_info["dateo"])

                if d < self.dateo_fallback:
                    print("sim date appears to be earlier than the start date")
                    print("falling back to the previous date of origin")
                    print(self._current_info["dt_seconds"].value / 60.0 / 60.0)
                    print(self.dateo_fallback, self._current_info["dateo"])
                    print(forecast_hour)
                    raise Exception()

                return d
            except Exception as exc:
                print(exc)
                raise Exception("problem when reading file {0}".format(self.path))
        else:
            raise Exception("No current info has been stored: please make sure you read some records first.")

    def get_datetime_for_the_last_read_record(self):
        """
         returns datetime object corresponding to the last read record
         """
        return self.get_cdf_datetime_for_the_last_read_record()

    def __get_datetime_for_the_last_read_record(self):
        """
        returns datetime object corresponding to the last read record
        """

        if self._current_info is not None:
            try:

                # extra can contain the validity date
                extra1 = self._current_info["extra1"].value
                if extra1 > 0:
                    date_s = self._dateo_to_string(extra1)
                    return datetime.strptime(date_s, self._dateo_format)

                forecast_hour = self.get_current_validity_date()
                assert forecast_hour >= 0

                if not hasattr(self, "dateo_fallback"):
                    self.dateo_fallback = self._current_info["dateo"]

                d = self._current_info["dateo"] + timedelta(hours=forecast_hour)
                print(d, forecast_hour, self._current_info["dateo"])

                if d < self.dateo_fallback:
                    print("sim date appears to be earlier than the start date")
                    print("falling back to the previous date of origin")
                    print(self._current_info["dt_seconds"].value / 60.0 / 60.0)
                    print(self.dateo_fallback, self._current_info["dateo"])
                    print(forecast_hour)
                    raise Exception()

                return d
            except Exception as exc:
                print(exc)
                raise Exception("problem when reading file {0}".format(self.path))
        else:
            raise Exception("No current info has been stored: please make sure you read some records first.")

    def get_4d_field_fc_hour_as_time(self, name="", level_kind=level_kinds.ARBITRARY, label=None):
        """
        Returns a map {forecast hour: {z: T(x,y)}}
        """
        result = {}
        data1 = self.get_first_record_for_name(name, label=label)
        while data1 is not None:
            level = self.get_current_level()
            time = self.get_current_validity_date()

            if time not in result:
                result[time] = {}

            time_slice = result[time]
            time_slice[level] = data1

            data1 = self.get_next_record()

        return result

        pass

    def get_4d_field(self, name="", level_kind=level_kinds.ARBITRARY, label=None):
        """
        returns a map
        {t: {z: T(x, y)}}
        """
        result = {}
        data1 = self.get_first_record_for_name(name, label=label)

        while data1 is not None:
            level = self.get_current_level()
            time = self.get_datetime_for_the_last_read_record()

            time_slice = result.get(time, {})
            if not len(time_slice):
                result[time] = time_slice

            time_slice[level] = data1

            data1 = self.get_next_record()

        return result

    def get_2D_field_on_all_levels(self, name='SAND'):
        """
        returns a map {level => 2d field}
        Use this method if you are sure that the field yu want to get has only one record per level
        """
        result = {}
        data1 = self.get_first_record_for_name(name)
        result[self.get_current_level()] = data1

        while data1 is not None:
            data1 = self.get_next_record()
            if data1 is not None:
                result[self.get_current_level()] = data1
        return result

    def get_ip1_from_level(self, level, level_kind=level_kinds.ARBITRARY):
        lev = c_float(level)
        lev_kind = c_int(level_kind)
        str_form = create_string_buffer(b'')
        ip1 = c_int(0)
        self._dll.convip_wrapper(byref(ip1), byref(lev), byref(lev_kind),
                                 byref(c_int(self.FROM_LEVEL_TO_IP1_MODE)), str_form, byref(c_int(0)))

        # x1 = self._dll.ip1_all_wrapper(lev, lev_kind)
        # assert x1 == ip1.value, "x1 = {0}, ip1.value = {1}".format(x1, ip1.value)
        return int(ip1.value)

    def write_2d_field_clean(self, data, properties=None):
        """
        This method is a wrapper that should be used from external callers
        @param data: numpy array 2D
        @param properties: a dict, contains variable attributes (no ctypes)
                attributes: name, level, level_kind ...
        """

        # Make the function work with the current_info dictionary
        if "varname" in properties:
            properties["name"] = properties["varname"]

        self.write_2D_field(data=data, **properties)

    def write_2D_field(self, name='', level=1, level_kind=level_kinds.ARBITRARY,
                       data=None, grid_type='Z', ig=None, ip=None, typ_var="P",
                       dateo="20120101000000", label="soil temp",
                       lon1=None, lat1=None,
                       lon2=None, lat2=None, npas=None, deet=None,
                       data_type=data_types.IEEE_floating_point,
                       nbits=-32, **kwargs
                       ):
        """
        Do not care about grid type just write data to the file
        int fstecr_wrapper(float* field, int bits_per_value, int iun,
                              int date, int deet, int npas,
                              int ni, int nj, int nk,
                              int ip1, int ip2, int ip3,
                              char *in_typvar, char *in_nomvar,
                              char *in_etiket, char *in_grtyp,
                              int ig1, int ig2, int ig3, int ig4,
                              int datyp, int rewrite)

        lon1, lat1, lon2, lat2 -are the parameters of the rotated lat lon (used only if grid_type = Z)
        Note: currently the datatypes of the input field is limited to the array of float32
        dateo could be passed as string and as int (in rpn format)
        :param level:
        :param name: name of the variable
        """

        if isinstance(name, bytes):
            name = name.decode()

        if isinstance(grid_type, bytes):
            grid_type = grid_type.decode()

        # Change nbits sign
        if nbits > 0:
            nbits *= -1

        if nbits == -32 or nbits == -16:
            data = data.astype(np.float32)
        elif nbits == -64:
            data = data.astype(np.float64)

        the_data = np.reshape(data, data.size, order='F')
        # if data_type == data_types.IEEE_floating_point and nbits == -32:
        # the_data = np.array(the_data, dtype = np.float32)
        # elif nbits == -16 and data_type == data_types.compressed_floating_point:
        # the_data = np.array(the_data, dtype = np.dtype("f2"))
        # elif nbits == -16:
        # the_data = np.array(the_data, dtype = np.float16 )

        nbits_c = c_int(nbits)

        if type(dateo) == int:
            date_c = c_int(dateo)
            if dateo:
                dateo_datetime = datetime.strptime(self._dateo_to_string(dateo), self._dateo_format)
            else:
                dateo_datetime = None
        elif type(dateo) == datetime:
            dateo_datetime = dateo
            dateo_s = dateo.strftime(self._dateo_format)
            date_c = self._string_to_dateo(dateo_s)
        elif type(dateo) == str:
            date_c = c_int(self._string_to_dateo(dateo))
            dateo_datetime = datetime.strptime(dateo, self._dateo_format)
        else:
            raise Exception("Unknown dateo format")

        deet = c_int(0) if deet is None else c_int(deet)
        npas = c_int(1) if npas is None else c_int(npas)
        nk = c_int(1) if len(data.shape) <= 2 else data.shape[2]

        if ip is None:
            ip1 = c_int(self.get_ip1_from_level(level, level_kind=level_kind))
            ip2 = c_int(0)
            ip3 = c_int(0)
        else:
            ip1, ip2, ip3 = map(c_int, ip)

        [ni, nj] = data.shape[:2]
        ni = c_int(ni)
        nj = c_int(nj)

        # figure out the ig values
        if None not in [lon1, lat1, lon2, lat2]:

            grid_type_for_coords = "E" if grid_type == "Z" else grid_type

            c_lon1, c_lat1, c_lon2, c_lat2 = map(c_float, [lon1, lat1, lon2, lat2])
            ig1, ig2, ig3, ig4 = map(c_int, [0, 0, 0, 0])

            self._dll.cxg_to_ig_wrapper(c_char_p(grid_type_for_coords.encode()),
                                        byref(ig1), byref(ig2), byref(ig3), byref(ig4),
                                        byref(c_lat1), byref(c_lon1), byref(c_lat2), byref(c_lon2))
            print(ig1, ig2, ig3, ig4)
        elif ig is not None:
            ig1, ig2, ig3, ig4 = map(c_int, ig)
        else:
            ig1, ig2, ig3, ig4 = map(c_int, [0, 0, 0, 0])

        typvar = create_string_buffer(typ_var.encode() if hasattr(typ_var, "encode") else typ_var)
        nomvar = create_string_buffer(name.encode() if hasattr(name, "encode") else name)
        etiket = create_string_buffer(label.encode() if hasattr(label, "encode") else label)
        grtyp = create_string_buffer(grid_type.encode() if hasattr(grid_type, "encode") else grid_type)
        datyp = c_int(data_type)
        rewrite = c_int(1)

        status = self._dll.fstecr_wrapper(the_data.ctypes.data_as(POINTER(c_float)),
                                          nbits_c, self._file_unit, date_c, deet, npas,
                                          ni, nj, nk,
                                          ip1, ip2, ip3, typvar, nomvar,
                                          etiket, grtyp,
                                          ig1, ig2, ig3, ig4,
                                          datyp, rewrite)

        # set current info

        self._current_info = {'ig': [ig1, ig2, ig3, ig4],
                              'ip': [ip1, ip2, ip3],
                              'shape': [ni, nj, nk],
                              'dateo': dateo_datetime,
                              'dt_seconds': deet,
                              'npas': npas,
                              'varname': nomvar,
                              "var_type": typvar,
                              "data_type": datyp,
                              "nbits": nbits_c,
                              "grid_type": grtyp,
                              "dateo_rpn_format": dateo
                              }

    def get_all_time_records_for_name(self, varname="STFL"):
        """
        Created for retrieving the fields corresponding to
        different times,
        works as self.get_3D_field, but instead of the map
        {level: 2d record} it returns the map {date: 2d record}
        Use this methond only in the case if you are sure that
        the field you are trying to read containsonly one record for each time step

        :return type: dict
        """
        result = {}
        data1 = self.get_first_record_for_name(varname)
        result[self.get_datetime_for_the_last_read_record()] = data1

        while data1 is not None:
            data1 = self.get_next_record()
            if data1 is not None:
                result[self.get_datetime_for_the_last_read_record()] = data1
        return result

    def get_all_time_records_for_name_and_level(self, varname="STFL", level=-1,
                                                level_kind=level_kinds.ARBITRARY):
        """
        Created for retrieving the fields corresponding to
        different times,
        works as self.get_3D_field, but instead of the map
        {level: 2d record} it returns the map {date: 2d record}
        Use this methond only in the case if you are sure that
        the field you are trying to read containsonly one record for each time step

        :return type: dict
        """
        result = {}
        data1 = self.get_first_record_for_name_and_level(varname, level=level, level_kind=level_kind)
        result[self.get_datetime_for_the_last_read_record()] = data1

        while data1 is not None:
            data1 = self.get_next_record()
            if data1 is not None:
                result[self.get_datetime_for_the_last_read_record()] = data1
        return result

    def get_time_records_iterator_for_name_and_level(self, varname="STFL", level=-1,
                                                     level_kind=level_kinds.ARBITRARY):
        """
        Created for retrieving the fields corresponding to
        different times,
        works as self.get_3D_field, but instead of the map
        {level: 2d record} it returns the map {date: 2d record}
        Use this methond only in the case if you are sure that
        the field you are trying to read contains only one record for each time step

        Warning it is not safe to use this RPN object while iterating over the generator

        :return type: generator object
        """

        data1 = self.get_first_record_for_name_and_level(varname, level=level, level_kind=level_kind)

        while data1 is not None:
            yield self.get_datetime_for_the_last_read_record(), data1
            data1 = self.get_next_record()

    def get_current_info(self):
        """
        return current info of just read record, returns values are not ctype objects
        """
        info_copy = {}
        for k, v in self._current_info.items():
            if hasattr(v, "value"):
                v = v.value
                if isinstance(v, bytes):
                    v = v.decode()
            if hasattr(v, "__iter__"):
                if hasattr(v[0], "value"):
                    v = [vi.value for vi in v]

            info_copy[k] = v

        return info_copy

    # implement with interface
    def __enter__(self):
        return self

    # implement with interface
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def test():
    # path = 'data/geophys_africa'
    path = 'data/pm1989010100_00000003p'
    rpnObj = RPN(path)
    precip = rpnObj.get_first_record_for_name("PR")

    import matplotlib.pyplot as plt

    plt.imshow(precip.transpose())
    plt.colorbar()
    plt.show()
    plt.savefig("precip.png")

    os.system("r.diag ggstat {0}".format(path))

    print("Min = {0}, Mean = {1}, Max = {2}, Var = {3}".format(np.min(precip), np.mean(precip), np.max(precip),
                                                               np.var(precip)))

    datev = rpnObj.get_current_validity_date()
    print('validity date = ', datev)
    print(rpnObj._current_info)
    print(rpnObj.get_number_of_records())
    rpnObj.get_longitudes_and_latitudes()
    rpnObj.close()


def test_get_all_records_for_name():
    path = "data/CORDEX/na/e1/pmNorthAmerica_0.44deg_CanHistoE1_A1950-1954-djf"
    rpnObj = RPN(path=path)
    date_to_field = rpnObj.get_4d_field(name="I0")

    lons2d1, lats2d1 = rpnObj.get_longitudes_and_latitudes_for_the_last_read_rec()
    lons2d2, lats2d2 = rpnObj.get_longitudes_and_latitudes()

    rpnObj.close()

    print(np.mean(lons2d1), np.mean(lats2d1))
    print(np.mean(lons2d2), np.mean(lats2d2))

    for t, v in date_to_field.items():
        for z, v1 in v.items():
            print(t, z, v1.min(), v1.mean(), v1.max())


def test_select_by_date():
    path = "/home/huziy/skynet3_rech1/test/snw_LImon_NA_CRCM5_CanESM2_historical_r1i1p1_185001-200512.rpn"

    rObj = RPN(path)
    rObj.suppress_log_messages()
    res = rObj.get_records_for_foreacst_hour(var_name="I5", forecast_hour=0)

    rObj.close()

    print(res.keys())


if __name__ == "__main__":
    # test_select_by_date()
    # test_dateo()
    # test()
    # test_get_all_records_for_name()
    print("Hello World")

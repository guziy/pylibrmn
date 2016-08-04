from __future__ import absolute_import
import glob
import os

from rpn import level_kinds
from rpn.rpn import RPN
import itertools
import numpy as np


class MultiRPN(object):
    def __init__(self, path=""):
        """
        Used to open multiple rpn  files for reading
        :param path: unix regular expression for the multiple paths
                ~ is expanded as well as environment variables ...
                Or a list or iterable of sequence of file paths to be joined
        """

        if isinstance(path, str):
            p1 = os.path.expanduser(path)  # expand the user if required '~'
            p2 = os.path.expandvars(p1)  # expand env vars if required

            self.path_list = glob.glob(p2)

            if len(self.path_list) == 0:
                raise IOError("No files found for {}".format(p2))

        else:
            try:
                self.path_list = list(sorted(path))
            except Exception:
                raise Exception("Was not able to recognize: {}".format(path))

        self._last_read_file = None

        # open linked rpn files
        self.linked_robj_list = []
        try:
            for fpath in self.path_list:
                self.linked_robj_list.append(RPN(fpath))
        except Exception as e:
            # Close opened files and forward the exception
            for r in self.linked_robj_list:
                r.close()
            raise e

        if len(self.linked_robj_list) == 0:
            raise IOError("Could not find files matching: {}".format(path))

    def get_number_of_records(self):
        """

        :return: Total number of records in linked files
        """
        return sum(r.get_number_of_records() for r in self.linked_robj_list)

    def get_first_record_for_name(self, varname):
        """

        :param varname:
        :return: the first record found in the files with the given variable name
        """
        field = None
        for r in self.linked_robj_list:
            try:
                field = r.get_first_record_for_name(varname=varname)
                self._last_read_file = r
                if field is not None:
                    return field
            except Exception:
                pass

        if field is None:
            raise Exception("{} is not found in {}".format(varname, ",".join(self.path_list)))

    def close(self):
        # close unused files
        for f in self.linked_robj_list:
            f.close()

    def get_4d_field(self, varname, level_kind=level_kinds.ARBITRARY):
        """
        Get the variable as a dict {date: {level: fie}}
        :param varname:
        :param level_kind:
        :return:
        """
        result = {}

        for f in self.linked_robj_list:
            try:
                result.update(f.get_4d_field(name=varname, level_kind=level_kind))
                self._last_read_file = f
            except Exception:
                pass

        return result

    def get_longitudes_and_latitudes_for_the_last_read_rec(self):
        return self.get_longitudes_and_latitudes_of_the_last_read_rec()

    def get_longitudes_and_latitudes_of_the_last_read_rec(self):
        """
        :return: (lons2d, lats2d) corresponding to the last record read from the files
        """

        # try to use the last file in  the list of linked objects
        if self._last_read_file is None and len(self.linked_robj_list) > 0:
            self._last_read_file = self.linked_robj_list[-1]

        if self._last_read_file is None:
            raise Exception("You have not read any data fields yet")

        return self._last_read_file.get_longitudes_and_latitudes_for_the_last_read_rec()

    def get_list_of_varnames(self):
        names = itertools.chain(*[r.get_list_of_varnames() for r in self.linked_robj_list])
        return np.unique(list(names))

    def get_all_time_records_for_name_and_level(self, varname="STFL", level=-1,
                                                level_kind=level_kinds.ARBITRARY):
        """
        Get all records for the specified variable name and level
        :returns dict with datetime objects as keys and data fields as values
        """
        result = {}
        for f in self.linked_robj_list:
            result.update(dict(f.get_time_records_iterator_for_name_and_level(varname=varname, level=level,
                                                                              level_kind=level_kind)))

        self._last_read_file = self.linked_robj_list[-1]
        return result


    def get_proj_parameters_for_the_last_read_rec(self):
        return self._last_read_file.get_proj_parameters_for_the_last_read_rec()

if __name__ == '__main__':
    mf = MultiRPN(path=os.path.expanduser("/home/${USER}/*.py"))
    print(mf.path_list)

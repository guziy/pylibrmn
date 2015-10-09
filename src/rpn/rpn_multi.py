import glob
import os

from rpn import level_kinds
from rpn.rpn import RPN


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
                raise FileNotFoundError("No files found for {}".format(p2))

            for p in self.path_list:
                if not os.path.isfile(p):
                    raise FileNotFoundError("File {} not found".format(p))
        else:
            try:
                self.path_list = list(path)
            except Exception:
                raise Exception("Was not able to recognize: {}".format(path))

        # open linked rpn files
        self.linked_robj_list = [RPN(fpath) for fpath in self.path_list]

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
            except Exception:
                pass

        return result

if __name__ == '__main__':
    mf = MultiRPN(path=os.path.expanduser("/home/${USER}/*.py"))
    print(mf.path_list)

__author__ = 'huziy'


from rpn.rpn import RPN
from rpn.tests.utils import get_input_file_path
import os

def test_read_ts_file():
    """
    Test if the module is capable of reading the files containing timeseries data

    """

    the_dir, script_name = os.path.split(__file__)
    in_path = get_input_file_path("erai_1980-2009_PR_ts.88", the_dir)

    r = RPN(in_path)
    pr = r.get_first_record_for_name("PR")
    print(pr.shape, pr.min(), pr.max(), pr.mean(), pr.std())

    r.close()






if __name__ == "__main__":
    test_read_ts_file()
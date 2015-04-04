import os
from rpn.rpn import RPN

__author__ = 'huziy'

from rpn.tests.utils import get_input_file_path

the_dir, script_name = os.path.split(__file__)
in_path = get_input_file_path("erai_1980-2009_PR_ts.88", the_dir)


def test_get_time_records_iterator_for_name_and_level(path=None):
    """
    Test if the iterator approach works
    @return:
    """


    path = in_path if path is None else path

    if not os.path.isfile(path):
        print("{} does not exist, so not performing tests with it.".format(path))
        return 0

    r = RPN(path)
    for d, f in r.get_time_records_iterator_for_name_and_level(varname="PR"):
        print(d, f.mean())

    print(r.get_current_info())
    r.close()


if __name__ == '__main__':
    test_get_time_records_iterator_for_name_and_level("../../../data/erai_1980-2009_PR_ts.88")
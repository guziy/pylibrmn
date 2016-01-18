from __future__ import absolute_import
import os
from nose.tools import ok_

__author__ = 'huziy'


from rpn.tests.utils import get_input_file_path

the_dir, script_name = os.path.split(__file__)
in_path = get_input_file_path("test.rpn", the_dir)


from rpn.rpn import RPN


def test_copy_records():
    """
    Test confirming that you cannot in the middle of the get_next_recod cycle take longitudes,
    and continue with getting next records

    """
    r = RPN(in_path)
    temp_file = "test1.rpn"
    r_out = RPN(temp_file, mode="w")
    n_in = r.get_number_of_records()
    n_out = 0
    data = []
    while data is not None:
        data = r.get_next_record()
        if data is None:
            break
        n_out += 1
        info = r.get_current_info()
        varname = info[RPN.VARNAME_KEY].strip()
        print(varname)
        if varname not in [">>", "^^"]:
            for i in range(10):
                r_out.write_2d_field_clean(data, properties=dict(name="X{0}".format(i), ip=info["ip"], ig=info["ig"]))

        r_out.write_2d_field_clean(data, properties=dict(name=varname, ip=info["ip"], ig=info["ig"],
                                                         grid_type=info[RPN.GRID_TYPE]))

    ok_(n_in == n_out, "Copied {0} recs, but there are {1} records".format(n_out, n_in))

    r.close()
    r_out.close()

    r = RPN(temp_file)
    r.get_next_record()
    print(r.get_current_info())
    r.get_longitudes_and_latitudes_for_the_last_read_rec()
    data = r.get_next_record()
    ok_(data is None)  # Should be None if there is only one coordinate record in the file
    r.close()
    os.remove(temp_file)
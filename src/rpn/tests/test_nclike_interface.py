from __future__ import absolute_import
from nose.tools import ok_
from nose import tools
from rpn.rpn import RPN


from rpn.tests.utils import get_input_file_path
import os

the_dir, script_name = os.path.split(__file__)
in_path = get_input_file_path("test.rpn", the_dir)


def test_getting_whole_field():
    """
    Get the whole field for a var
    """
    with RPN(in_path) as r:
        data = r.variables["I5"][:]

    assert len(data.shape) == 4, "data.shape={}".format(data.shape)

def test_getting_a_point():
    """
    Extract 1point
    """
    with RPN(in_path) as r:
        var = r.variables["I5"]
        shape = var.shape
        nx, ny = shape[-2:]


        data1 = var[0, 0, nx // 2, ny // 2]


        data = var[:]

        expect = data.squeeze()[nx // 2, ny // 2]
        assert expect == data1, "got {}, but expect {}, ".format(data1, expect)



def test_getting_var_info_without_reading_in_memory():
    with RPN(in_path) as r:
        var = r.variables["I5"]
        expected_shape = (1, 1, 46, 46)
        msg = "expect: {}, but got {}".format(expected_shape, var.shape)
        ok_(var.shape == expected_shape, msg=msg)


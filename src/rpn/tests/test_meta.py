
import os


from rpn.rpn import RPN

from rpn.tests.utils import get_input_file_path

from nose.tools import ok_

the_dir, script_name = os.path.split(__file__)
in_path = get_input_file_path("metas.rpn", the_dir)


def test_read_meta_records():
    with RPN(in_path) as r:
        m = r.get_first_record_for_name_and_level(varname="META", level=1)

        s = "".join([chr(c) for c in m])

        ok_(m.shape[0] == 1104, "Wrong array shape: {}".format(m.shape))

        ok_("MaskUSGS" in s, msg="""Extracted \n --------------------- \n {} \n --------------------- \n """.format(s))


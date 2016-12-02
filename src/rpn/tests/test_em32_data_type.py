
import os
from rpn.rpn import RPN
from rpn.tests.utils import get_input_file_path
from nose.tools import ok_

import numpy as np

the_dir, scriptname = os.path.split(__file__)
in_file_path = get_input_file_path("CRU_interpolado_big", the_dir)


def test_em32_dtype():
    r = None
    try:
        r = RPN(in_file_path)
        pr = r.get_first_record_for_name("PR")
        pr = np.ma.masked_where(pr > 1e30, pr)

        vranges = (pr.max(), pr.min(), pr.mean())
        msg = "Total precipitation (M/s) should not be greater than 1, but pr.max() = {}; pr.min() = {}; pr.mean() = {}".format(*vranges)

        ok_(pr.max() < 1, msg=msg)

    finally:
        if r is not None:
            r.close()
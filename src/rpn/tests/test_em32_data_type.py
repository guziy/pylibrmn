
import os
from rpn.rpn import RPN
from rpn.tests.utils import get_input_file_path
from nose.tools import ok_, assert_almost_equal

import numpy as np

the_dir, scriptname = os.path.split(__file__)
in_file_path = get_input_file_path("CRU_interpolado_big", the_dir)


def check_point(sel_indices, expected_val, pr):
    msg = "pr[{},{}]={}, but {} is expected".format(sel_indices[0], sel_indices[1], pr[sel_indices], expected_val)
    assert_almost_equal(pr[sel_indices], expected_val, places=12, msg=msg)


def test_em32_dtype():
    r = None
    try:
        r = RPN(in_file_path)
        pr = r.get_first_record_for_name("PR")
        pr = np.ma.masked_where(pr > 1e30, pr)

        vranges = (pr.max(), pr.min(), pr.mean())
        msg = "Total precipitation (M/s) should not be greater than 1, but pr.max() = {}; pr.min() = {}; pr.mean() = {}".format(*vranges)

        ok_(pr.max() < 1, msg=msg)

        sel_indices = [(70, 23), (68, 146)]
        expected_vals = [2.8792e-8, 9.3780e-9] # taken from xrec

        for inds, exp_val in zip(sel_indices, expected_vals):
            check_point(inds, exp_val, pr)

    finally:
        if r is not None:
            r.close()
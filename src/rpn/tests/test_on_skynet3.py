from __future__ import absolute_import
import os
from nose.tools import ok_
from rpn.rpn import RPN
import subprocess
__author__ = 'huziy'


def test_nbits24():
    path = "/skynet3_rech1/huziy/geophys_West_NA_0.25deg_144x115.fst"

    if not os.path.isfile(path):
        return

    r = RPN(path=path)
    data = r.get_first_record_for_name_and_level(varname="VF", level=2)

    print(data.shape, data.max(), data.min(), data.mean(), data.var())
    ok_(data.max() <= 1)

    proc = subprocess.Popen(["r.diag", "ggstat", path], stdout=subprocess.PIPE)
    (out, err) = proc.communicate()
    if err != 0:
        print("Warning: Could not find r.diag, this is not critical, but some tests will not be run.")
        return

    lines = out.split("\n")
    lines = filter(lambda line: ("VF" in line) and ("2 ar" in line), lines)

    fields = lines[0].split()

    the_mean = float(fields[12])
    the_var = float(fields[13])
    ok_(abs(data.mean() - the_mean) < 1e-6, msg="The mean does not correspond to ggstat")
    ok_(abs(data.var() - the_var) < 1e-6, msg="The variance does not correspond to ggstat")

    r.close()


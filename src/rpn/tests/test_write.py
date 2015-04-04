import subprocess
from rpn import data_types

__author__ = 'huziy'

from rpn.rpn import RPN
import numpy as np
import os
from nose.tools import ok_


def test_write_rpn_32():
    wfile = "test.rpn"
    r = RPN(wfile, mode="w")
    nx = ny = 10
    arr = np.zeros((nx, ny), dtype=np.float32)
    for i in range(nx):
        for j in range(ny):
            arr[i, j] = i ** 2 + j ** 2

    r.write_2D_field(
        name="TEST", data=arr
    )
    r.close()

    proc = subprocess.Popen(["r.diag", "ggstat", wfile], stdout=subprocess.PIPE)
    (out, err) = proc.communicate()

    print(out)
    out = out.decode()
    ok_("{:E}".format(arr.max()) in out, "Could not find the max={:E} in {}".format(arr.max(), out))
    ok_("{:E}".format(arr.min()) in out, "Could not find the min={:E} in {}".format(arr.min(), out))
    ok_("{:E}".format(arr.mean()) in out, "Could not find the mean={:E} in {}".format(arr.mean(), out))
    ok_("{}".format(32) in out, "Could not find 32 in the ggstat output")
    print("{:E}".format(arr.mean()), "{:E}".format(arr.min()), "{:E}".format(arr.max()))
    os.remove(wfile)


def test_write_rpn_compressed():
    wfile = "test.rpn"
    r = RPN(wfile, mode="w")
    nx = ny = 10
    arr = np.zeros((nx, ny), dtype="f4")
    for i in range(nx):
        for j in range(ny):
            arr[i, j] = i ** 2 + j ** 2

    r.write_2D_field(
        name="TEST", data=arr, data_type=data_types.compressed_floating_point, nbits=-16
    )
    r.close()

    proc = subprocess.Popen(["r.diag", "ggstat", wfile], stdout=subprocess.PIPE)
    (out, err) = proc.communicate()

    out = out.decode()
    print(out)
    print(type(out), type("some str"))
    ok_("{:E}".format(arr.max()) in out, "Could not find the max={:E} in {}".format(arr.max(), out))
    ok_("{:E}".format(arr.min()) in out, "Could not find the min={:E} in {}".format(arr.min(), out))
    ok_("{:E}".format(arr.mean()) in out, "Could not find the mean={:E} in {}".format(arr.mean(), out))
    ok_("{}".format(16) in out, "Could not find 16 in the ggstat output")
    print("{:E}".format(arr.mean()), "{:E}".format(arr.min()), "{:E}".format(arr.max()))

    os.remove(wfile)


if __name__ == '__main__':
    test_write_rpn_32()
import subprocess

__author__ = 'huziy'


from rpn.rpn import RPN
import numpy as np
import os
from nose.tools import ok_


def test_write_rpn():
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

    print out

    ok_("{:E}".format(arr.max()) in out, "Could not find the max={:E} in {}".format(arr.max(), out))
    ok_("{:E}".format(arr.min()) in out, "Could not find the min={:E} in {}".format(arr.min(), out))
    ok_("{:E}".format(arr.mean()) in out, "Could not find the mean={:E} in {}".format(arr.mean(), out))

    os.remove(wfile)




if __name__ == '__main__':
    test_write_rpn()
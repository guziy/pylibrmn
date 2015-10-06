import os

import numpy as np
from nose import tools

from rpn import data_types
from rpn.rpn import RPN
from rpn.rpn_multi import MultiRPN

FILE_NAMES = ["test_{}.rpn".format(i) for i in range(5)]


def create_files():
    for f in FILE_NAMES:
        r = RPN(f, mode="w")
        nx = ny = 10
        arr = np.zeros((nx, ny), dtype="f4")
        for i in range(nx):
            for j in range(ny):
                arr[i, j] = i ** 2 + j ** 2

        r.write_2D_field(
            name="TEST", data=arr, data_type=data_types.compressed_floating_point, nbits=-16
        )
        r.close()


def delete_files():
    for f in FILE_NAMES:
        if os.path.isfile(f):
            os.remove(f)


def test_get_number_of_records():
    create_files()
    r = MultiRPN("test_?.rpn")

    tools.ok_(r.get_number_of_records(), len(FILE_NAMES))

    r.close()


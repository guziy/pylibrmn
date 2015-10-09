import os

import numpy as np
from nose import tools

from rpn import data_types
from rpn.rpn import RPN
from rpn.rpn_multi import MultiRPN

FILE_NAMES = ["test_{}.rpn".format(i) for i in range(5)]


def create_files():
    for nf, f in enumerate(FILE_NAMES):
        r = RPN(f, mode="w")
        nx = ny = 10
        arr = np.zeros((nx, ny), dtype="f4")
        for i in range(nx):
            for j in range(ny):
                arr[i, j] = i ** 2 + j ** 2

        r.write_2D_field(
            name="T{}".format(nf), data=arr, data_type=data_types.compressed_floating_point, nbits=-16
        )
        r.close()


def create_files_with_same_var_for_different_times(vname="T"):
    for nf, f in enumerate(FILE_NAMES):
        r = RPN(f, mode="w")
        nx = ny = 10
        arr = np.zeros((nx, ny), dtype="f4")
        for i in range(nx):
            for j in range(ny):
                arr[i, j] = i ** 2 + j ** 2

        r.write_2D_field(
            name=vname, data=arr, data_type=data_types.compressed_floating_point, nbits=-16,
            ip=[0, 10 * nf, 0], npas=nf + 1, deet=600
        )
        r.close()


def delete_files():
    for f in FILE_NAMES:
        if os.path.isfile(f):
            os.remove(f)

# Tests


def test_get_number_of_records():
    r = None
    try:

        create_files()
        r = MultiRPN("test_?.rpn")
        msg = "Number of records should be equal to the total number in all files"
        tools.assert_equals(r.get_number_of_records(), len(FILE_NAMES), msg)

    finally:
        if r is not None:
            r.close()

        delete_files()


def test_should_find_all_records():
    r = None
    try:

        create_files()
        r = MultiRPN("test_?.rpn")

        for fn in range(len(FILE_NAMES)):
            rec = r.get_first_record_for_name("T{}".format(fn))
            print("file {} - OK".format(fn))
            print(rec.mean(), rec.shape)

    finally:
        if r is not None:
            r.close()

        delete_files()


def test_get_4d_field():
    r = None
    vname = "T"

    try:

        create_files_with_same_var_for_different_times(vname=vname)
        r = MultiRPN("test_?.rpn")

        recs = r.get_4d_field(vname)
        msg = "Not all records for {} were found".format(vname)
        print(recs.keys())
        tools.assert_equals(len(FILE_NAMES), len(recs), msg)



    finally:

        if r is not None:
            r.close()

        delete_files()

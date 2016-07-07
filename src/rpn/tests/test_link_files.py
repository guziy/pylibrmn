from __future__ import absolute_import
import os
import numpy as np
from nose import tools
from rpn.tests.utils import get_input_file_path

from rpn import data_types
from rpn.rpn import RPN
from rpn.rpn_multi import MultiRPN

FILE_NAMES = ["test_{}.rpn".format(i) for i in range(5)]


def create_files(fnames=FILE_NAMES):
    for nf, f in enumerate(fnames):
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


def create_files_with_same_var_for_different_times(vname="T", fnames=FILE_NAMES):
    for nf, f in enumerate(fnames):
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


def delete_files(fnames=FILE_NAMES):
    for f in fnames:
        if os.path.isfile(f):
            os.remove(f)


the_dir, script_name = os.path.split(__file__)
in_path = get_input_file_path("test.rpn", the_dir)


# Tests


def test_can_link_many_files(nfiles=200):
    many_fnames = ["test_{}.rpn".format(i) for i in range(nfiles)]

    r = None
    try:
        create_files(fnames=many_fnames)

        r = MultiRPN("test_*.rpn")

        tools.assert_greater(r.get_number_of_records(), 0, msg="There should be more than 0 records")

    finally:
        if r is not None:
            r.close()

        delete_files(fnames=many_fnames)


def test_can_link_1000_files():
    test_can_link_many_files(900)


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



def test_get_list_of_varnames():
    r = None
    vname = "T"

    try:

        create_files_with_same_var_for_different_times(vname=vname)
        r = MultiRPN("test_?.rpn")

        msg = "the list of varnames should contain {}".format(vname)
        vnames = r.get_list_of_varnames()

        tools.assert_in(vname, vnames, msg)
        tools.assert_equal(len(vnames), 1, "There is only one unique field name in the files")

    finally:
        if r is not None:
            r.close()

        delete_files()



def test_getting_coordinates_for_the_last_read_record_should_not_fail():
    r = None
    try:

        r = MultiRPN(in_path)
        rec = r.get_first_record_for_name("I5")
        lons, lats = r.get_longitudes_and_latitudes_of_the_last_read_rec()
        tools.assert_equals(lons.shape, lats.shape, "Shapes of lon and lat arrays should be the same.")

    finally:
        if r is not None:
            r.close()

        delete_files()

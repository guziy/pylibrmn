from __future__ import absolute_import

__author__ = 'huziy'

import os
from rpn.tests.utils import get_input_file_path

the_dir, script_name = os.path.split(__file__)
in_path = get_input_file_path("test.rpn", the_dir)

from rpn.rpn import RPN
from nose.tools import ok_
import numpy as np

import shutil

def test_append_existing_rpn_file():

    vname = "I5"

    r0 = RPN(in_path)
    data = r0.get_first_record_for_name(vname)
    r0.close()

    tmp_to_append = in_path + "_to_append"



    try:
        # copy the initial file
        shutil.copy(in_path, tmp_to_append)

        new_vname = "I5AP"
        r = RPN(tmp_to_append, mode="a")
        r.write_2D_field(name=new_vname, data=data)
        r.close()

        r1 = RPN(tmp_to_append)
        vlist = r1.get_list_of_varnames()

        ok_(vname in vlist, "The appended file does not contain {}, whereas the initial contained it ...".format(vname))
        ok_(new_vname in vlist, "Newly appended variable is not in the resulting file".format(vname))

        data1 = r1.get_first_record_for_name(new_vname)

        ok_(np.array_equal(data, data1), "Appended array is not the same as the initial one. max(|delta|) = {}".format(np.abs(data - data1).max()))

        r1.close()

    finally:
        os.remove(tmp_to_append)


from __future__ import absolute_import
import os
from nose.tools import ok_

__author__ = 'huziy'


from rpn.tests.utils import get_input_file_path
import numpy as np

the_dir, script_name = os.path.split(__file__)
in_path = get_input_file_path("test.rpn", the_dir)

in_path_g_grid = get_input_file_path("test_G_grid.rpn", the_dir)
verif_lonlats_g_grid = get_input_file_path("G_grid_LOLA.rpn", the_dir)


from rpn.rpn import RPN


def test_G_grid():

    with RPN(verif_lonlats_g_grid) as r:
        lons_verif = r.get_first_record_for_name("LO")
        lats_verif = r.get_first_record_for_name("LA")


    with RPN(in_path_g_grid) as r:
        var_names = r.get_list_of_varnames()

        data = r.get_first_record_for_name(varname=var_names[0])

        lons, lats = r.get_longitudes_and_latitudes_for_the_last_read_rec()


        epsilon = 1e-10
        epsilon_relax = 1e-5

        ok_(np.abs(lons[0, :].min()) <= epsilon, "The first longitude is not 0, but {}".format(lons[0, :].min()))
        ok_(np.abs(lons[0, :].max()) <= epsilon, "The first longitude is not 0, but {}".format(lons[0, :].max()))

        ok_(data.shape == lons.shape, "Lons shape ({}) is not equal to the data shape ({})".format(lons.shape, data.shape))
        ok_(data.shape == lats.shape, "Lats shape ({}) is not equal to the data shape ({})".format(lats.shape, data.shape))



        # ok_(np.min(np.abs(lats)) > epsilon, "The grid should not contain points on the equator")
        # ok_(np.min(np.abs(lats) - 90) > epsilon, "The grid should not contain points on the pole")



        max_error = np.abs(lons - lons_verif).max()
        ok_(max_error < epsilon, "max error in lons is more than eps (eps={}): {}".format(epsilon, max_error))

        max_error = np.abs(lats - lats_verif).max()
        ok_(max_error < epsilon_relax, "max error in lats is more than eps (eps={}): {}".format(epsilon, max_error))


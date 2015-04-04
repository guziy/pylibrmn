__author__ = 'huziy'

import os
from rpn.tests.utils import get_input_file_path

the_dir, script_name = os.path.split(__file__)
in_path = get_input_file_path("test.rpn", the_dir)

from rpn.rpn import RPN


def test_basemap_integration():
    """
    Basemap integration test: makes sense only if you have basemap installed
    """

    from rpn.domains.rotated_lat_lon import RotatedLatLon

    vname = "I5"
    # open the rpn file
    r = RPN(in_path)

    # read a field
    data = r.get_first_record_for_name(vname)
    print(data.shape)

    # get longitudes and latitudes fields
    lons2d, lats2d = r.get_longitudes_and_latitudes_for_the_last_read_rec()
    print(lons2d.shape)
    print("lon ranges: ", lons2d.min(), lons2d.max())

    # get projection parameters
    params = r.get_proj_parameters_for_the_last_read_rec()

    # create projection object
    print(params)
    rll = RotatedLatLon(**params)

    # Get the basemap object for the projection and domain defined by the coordinates
    b = rll.get_basemap_object_for_lons_lats(lons2d, lats2d)
    print(type(lons2d))
    x, y = b(lons2d, lats2d)
    b.drawcoastlines()
    img = b.pcolormesh(x, y, data)
    b.colorbar(img)


if __name__ == '__main__':
    in_path = "../../../" + in_path
    print(in_path)
    test_basemap_integration()
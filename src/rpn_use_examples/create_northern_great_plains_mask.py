import numpy as np
from osgeo import osr, ogr

# for reading and writing rpn files
from rpn.rpn import RPN
from rpn import data_types

# speed up
from numba import jit

## Input parameters

input_rpn_file="dm_NA_0.11deg.rpn"
input_shp_file="NGP/poly4_project.shp"
output_rpn_file="NGP_mask.rpn"

# =============================================


def get_lon_lat_fields_from_rpn(rpn_path="dm_NA_0.11deg.rpn"):
    r = RPN(rpn_path)

    var_names = r.get_list_of_varnames()
    sel_name = None
    for vname in var_names:
        if vname not in [">>", "^^", "HY"]:
            sel_name = vname
            break

    r.get_first_record_for_name(sel_name)
    lons, lats = r.get_longitudes_and_latitudes_for_the_last_read_rec()
    r.close()
    return lons, lats
        




def get_mask_from_shape(lons2d, lats2d, shp_path=""):
    """
    Get the 2d mask with 1 for points inside the polygon and 0 outside the polygon
    """

    ogr.UseExceptions()

    driver = ogr.GetDriverByName("ESRI Shapefile")
    datastore = driver.Open(shp_path, 0)
    layer = datastore.GetLayer(0)

    latlong = osr.SpatialReference()
    latlong.ImportFromProj4("+proj=latlong")

    ct = osr.CoordinateTransformation(latlong, layer.GetSpatialRef())

    print(layer.GetFeatureCount())

    ##read features from the shape file
    feature = layer.GetNextFeature()
    i = 0
   
    lons2d[lons2d > 180] -= 360
 
    the_mask = np.zeros(lons2d.shape, dtype=np.int)
    nx, ny = lons2d.shape
    # iterate all features in the layer
    while feature:
        # get the geometry of the feature
        geom = feature.GetGeometryRef()
 
        
        for ix in range(nx):
            if ix % 10 == 0:
                print("{}/{}".format(ix + 1, nx))
            for jy in range(ny):
                # Create the geometry for the center of the grid point (i, j)
                p = ogr.CreateGeometryFromWkt("POINT({} {})".format(lons2d[ix, jy], lats2d[ix, jy]))
                
                # project coordinates to the coordinate system of the shape file
                p.Transform(ct)

                the_mask[ix, jy] = geom.Contains(p)

        feature = layer.GetNextFeature()

        i += 1

    datastore.Destroy()
    return the_mask

def save_mask_to_rpn(mask_field, in_file="", out_file=""):
    
    rin = RPN(in_file)
    rout = RPN(out_file, mode="w")


    # Read coordinates and reshape(needed for writing)
    x = rin.get_first_record_for_name(">>")
    x.shape = (-1, 1)
    print(x.shape)


    y = rin.get_first_record_for_name("^^")
    y.shape = (1, -1)

    # get parameters of the last read record
    coord_info = rin.get_current_info()

    print(coord_info)

    # write coordinates
    coord_info.update({"name": ">>", "label": "NGP", "typ_var": "X", "nbits": -coord_info["nbits"]})
    rout.write_2d_field_clean(x, properties=coord_info)

    coord_info.update({"name": "^^"})
    rout.write_2d_field_clean(y, properties=coord_info)

    # write the mask
    rout.write_2d_field_clean(mask_field, properties=dict(name="FMSK", label="NGP_MASK", ig=coord_info["ip"] + [0,]))

    rin.close()
    rout.close()

# The main function 
def main():
    lons2d, lats2d = get_lon_lat_fields_from_rpn(rpn_path=input_rpn_file)
    the_mask = get_mask_from_shape(lons2d, lats2d, shp_path=input_shp_file)
    save_mask_to_rpn(the_mask, in_file=input_rpn_file, out_file=output_rpn_file)
    

# Entry point of the script
if __name__ == "__main__":
    main()





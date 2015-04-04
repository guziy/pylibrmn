# coding=utf-8
__author__ = 'huziy'
import numpy as np
from math import *

SOUTHERN_HEM = 2
NORTHERN_HEM = 1


def get_longitudes_and_latitudes_2d_for_ps_grid(pole_i, pole_j, d60, dgrw, ni, nj, hemisphere=NORTHERN_HEM):
    """
    These grids are defined by the parameters PI, PJ, D60 and DGRW.
    pole_i (starting with 1): Horizontal position of the pole, in grid points, from bottom left corner (1,1).
    pole_j (starting with 1): Vertical position of the pole, in grid points, from bottom left corner (1,1).
    d60: grid length, in meters, at 60° of latitude.
    dgrw: angle (between 0 and 360, +ve counterclockwise) between the Greenwich meridian and the horizontal axis
    of the grid.
    ni: number of grid cells in horizontal direction
    nj: number of grid cells in vertical direction
    """
    _pole_i = pole_i - 1  # use 0-based indicies
    _pole_j = pole_j - 1

    # coordinates of the lower left corner of the grid(center of thta gridcell actually)
    x0 = -_pole_i * d60
    y0 = -_pole_j * d60

    x1d = np.arange(x0, x0 + ni * d60, d60)
    y1d = np.arange(y0, y0 + nj * d60, d60)

    y2d, x2d = np.meshgrid(y1d, x1d)

    x_flat, y_flat = x2d.flatten(), y2d.flatten()
    lat_lon = [psxy2latlon(x, y, dgrw, xhem=hemisphere) for x, y in zip(x_flat, y_flat)]
    lat_lon = np.asarray(lat_lon)

    lon2d = lat_lon[:, 1]
    lon2d.shape = x2d.shape

    lat2d = lat_lon[:, 0]
    lat2d.shape = y2d.shape

    return lon2d, lat2d


def psxy2latlon(x, y, xaxis, xhem=NORTHERN_HEM):
    """
    Convert ps (x, y) coordinates to lat lon
    are relative indices to Pole
    d60 - in meters
    xaxis - in degrees (W???)   - rotation of the grid to the west
    DGRW: angle (between 0 and 360, +ve counterclockwise) between the Greenwich meridian and the horizontal
    axis of the grid
    """
    TRUE_LAT = 60.0
    RE = 6.371e6 * (1 + sin(np.radians(TRUE_LAT)))
    RE2 = pow(RE, 2)
    x = float(x)
    y = float(y)
    if x == 0 and y == 0:
        lat = 90
        lon = 0
    else:
        if x == 0:
            lon = y / abs(y) * 90.0
        else:
            lon = np.degrees(np.arctan2(y, x))

        lon = lon - xaxis  # /*Longitude*/
        if lon < -180:
            lon += 360.0
        ##        if lon < 0:
        ##           lon = lon + 360;
        R2 = pow(x, 2) + pow(y, 2)  # /*Latitude*/
        ADLAT = (RE2 - R2) / (RE2 + R2)  # /*Latitude*/
        lat = np.degrees(asin(ADLAT))  # /*Latitude*/

    if xhem == SOUTHERN_HEM:
        lat = -lat
        lon = -lon
    return lat, lon
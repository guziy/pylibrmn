import math

__author__ = "huziy"
__date__ = "$13 juil. 2010 13:34:52$"

from math import atan2
import numpy as np

EARTH_RADIUS_METERS = 0.637122e7  # mean earth radius used in the CRCM5 model for area calculation


# longitude and latitude are in radians
def get_nvector(rad_lon, rad_lat):
    return [np.cos(rad_lat) * np.cos(rad_lon), np.cos(rad_lat) * np.sin(rad_lon), np.sin(rad_lat)]


# p1 and p2 are geopoint objects
def get_distance_in_meters(*arg):
    """
    arg = point1, point2
    arg = lon1, lat1, lon2, lat2
    """
    if len(arg) == 2:  # if we have 2 geopoints as an argument
        [p1, p2] = arg
        n1 = p1.get_nvector()
        n2 = p2.get_nvector()
    elif len(arg) == 4:  # if we have the coordinates of two points in degrees
        x = np.radians(arg)
        n1 = get_nvector(x[0], x[1])
        n2 = get_nvector(x[2], x[3])
    else:
        raise Exception("get_distance_in_meters should be 2 or 4 parameters.")
    return EARTH_RADIUS_METERS * get_angle_between_vectors(n1, n2)


def get_angle_between_vectors(n1, n2):
    dy = np.cross(n1, n2)
    dy = np.dot(dy, dy) ** 0.5
    dx = np.dot(n1, n2)
    return atan2(dy, dx)


def lon_lat_to_cartesian(lon, lat, r_earth=EARTH_RADIUS_METERS):
    """
    calculates x,y,z coordinates of a point on a sphere with
    radius R = EARTH_RADIUS_METERS
    """
    lon_r = np.radians(lon)
    lat_r = np.radians(lat)

    x = r_earth * np.cos(lat_r) * np.cos(lon_r)
    y = r_earth * np.cos(lat_r) * np.sin(lon_r)
    z = r_earth * np.sin(lat_r)
    return x, y, z


def cartesian_to_lon_lat(x):
    """
     x - vector with coordinates [x1, y1, z1]
     returns [lon, lat]
    """

    lon = np.arctan2(x[1], x[0])
    lon = np.degrees(lon)
    lat = np.arcsin(x[2] / (np.dot(x, x)) ** 0.5)
    lat = np.degrees(lat)
    return lon, lat


# nvectors.shape = (3, nx, ny)
def get_coefs_between(nvectors1, nvectors2):
    return np.array([1.0 / (get_angle_between_vectors(v1, v2) * EARTH_RADIUS_METERS ) ** 2.0 for v1, v2 in
                     zip(nvectors1, nvectors2)])


if __name__ == "__main__":
    print("Hello World")

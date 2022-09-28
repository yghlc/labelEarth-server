#!/usr/bin/env python
# Filename: vectorData_io.py 
"""
introduction: reading and writting vector data.
A similar in https://github.com/yghlc/DeeplabforRS/blob/master/vector_gpd.py

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 17 April, 2022
"""
import geopandas as gpd

def read_a_vector_file(file_path):
    return gpd.read_file(file_path)

def get_polygon_centroid(polygon):
    # return the geometric center of a polygon
    return polygon.centroid

def get_centroid_imagebound_latlon(bound_path):
    geo_pd = read_a_vector_file(bound_path)
    # print(geo_pd.crs)
    # reproject
    geo_pd = geo_pd.to_crs('EPSG:4326') # now, gpd.__version__ >= '0.7.0'
    # if gpd.__version__ >= '0.7.0':
    #     geo_pd = geo_pd.to_crs('EPSG:4326')
    # else:
    #     geo_pd  = geo_pd.to_crs({'init':'EPSG:4326'})
    polygons = geo_pd.geometry.values
    # should only have one
    if len(polygons) != 1:
        raise ValueError('multiple polgyons in %s'%bound_path)
    return get_polygon_centroid(polygons[0])

if __name__ == '__main__':
    pass

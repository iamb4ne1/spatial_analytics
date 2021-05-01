# -*- coding: utf-8 -*-
"""
Created on Sun Apr 11 20:03:42 2021

@author: mark
"""


import geopandas as gpd
import pandas as pd

from efd_load_shapefile import load_files
from matplotlib import pyplot as plt

""" Files Required:
    1) Land cover
    2) LZ - target variable
    3) distance to water - large lakes AKA lake malawi, (rivers not useful)
    4) LZ income sources from John
    5) topography
    6) distance to market
"""

malawi_land_shapefile = r"C:\Users\mat4m_000\Documents\Wellow data\EfD\mwi_gc_adg"
malawi_land_gdf = gpd.GeoDataFrame.from_file(malawi_land_shapefile)

"""
fig, ax = plt.subplots()
malawi_land_gdf.AREA_M2.hist(ax=ax, bins=100, bottom=0.1)
ax.set_yscale('log')
"""

path_to_load = r'C:\Users\mat4m_000\Documents\Wellow data\EfD\SHAPESTOSEND\malawi'
lz_gdf_dict = load_files(path_to_load)
lz_gdf = pd.concat(lz_gdf_dict, ignore_index=True)

africa_lakes_path = r'C:\Users\mat4m_000\Documents\Wellow data\EfD\africawaterbody'
africa_lakes_gdf = gpd.GeoDataFrame.from_file(africa_lakes_path )

#malawi_land_gdf['centr_x'] = malawi_land_gdf['geometry'].centroid.x
#malawi_land_gdf['centr_y'] = malawi_land_gdf['geometry'].centroid.y
malawi_land_gdf['centroid'] = malawi_land_gdf['geometry'].centroid

malawi_land_gdf['centroid'].distance(africa_lakes_gdf)
africa_lakes_gdf[africa_lakes_gdf.NAME_OF_WA == 'Malawi'].boundary.distance(malawi_land_gdf) 

africa_boundaries = r"C:\Users\mat4m_000\Documents\Wellow data\EfD\africa_boundaries"
africa_boundaries_gdf = gpd.GeoDataFrame.from_file(africa_boundaries)
malawi_border = africa_boundaries_gdf[africa_boundaries_gdf.NAME_0 == 'Malawi' ]

malawi_lakes = gpd.sjoin(africa_lakes_gdf, malawi_border, how='inner', 
                         op='intersects', ## is this correct?
                         lsuffix='_l', rsuffix='_r')

pop = r"C:\Users\mat4m_000\Documents\Wellow data\EfD\malawi_pop_density_2015"
pop_gdf = gpd.GeoDataFrame.from_file(africa_boundaries)



from shapely import affinity
from scipy.spatial import Voronoi

def shape_to_points(shape, num = 10, smaller_versions = 10):
    points = []

    # Take the shape, shrink it by a factor (first iteration factor=1), and then 
    # take points around the contours
    for shrink_factor in range(0,smaller_versions,1):
        # calculate the shrinking factor
        shrink_factor = smaller_versions - shrink_factor
        shrink_factor = shrink_factor / float(smaller_versions)
        # actually shrink - first iteration it remains at 1:1
        smaller_shape = affinity.scale(shape, shrink_factor, shrink_factor)
        # Interpolate numbers around the boundary of the shape
        for i in range(0,int(num*shrink_factor),1):
            i = i / int(num*shrink_factor)
            x,y =  smaller_shape.interpolate(i, normalized=True).xy
            points.append( (x[0],y[0]))
    
    # add the origin
    x,y = smaller_shape.centroid.xy
    points.append( (x[0], y[0]) ) # near, but usually not add (0,0)
    
    points = np.array(points)
    return points


def points_to_voronoi(points):
    vor = Voronoi(points)
    vertices = [ x for x in vor.ridge_vertices if -1 not in x]
    # For some reason, some vertices were seen as super, super long. Probably also infinite lines, so take them out
    lines = [ LineString(vor.vertices[x]) for x in vertices if not vor.vertices[x].max() > 50000]
    return MultiLineString(lines)

#!/usr/bin/env python
# Filename: image_names_inExent 
"""
introduction: get the list of image name within an extent

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 28 September, 2022
"""

import os, sys
from optparse import OptionParser
import pandas as pd
import json

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR.absolute()))

from add_image_to_database import read_image_list

from vectorData_io import read_polygons_latlon
from vectorData_io import read_polygons_epsg3413

def b_anyone_within_extents(polygons, ext_polys):
    # if any one in polygons, within or intersect with anyone in ext_polys, then return True
    for poly in polygons:
        # if poly.is_valid is False:
        #     poly = poly.buffer(0.1)
        # print(poly)
        for ext in ext_polys:
            # print(ext)
            # if ext.is_valid is False:
            #     ext = ext.buffer(0.1)
            inter = ext.intersection(poly)
            if inter.is_empty is False:
                return True
    return False

def get_index_within_extent(ext_shp, image_object_paths, min_overlap_area=None):

    # read polygons to "EPSG:4326"  # not working
    # read to read all polygons to a planar coordinates (e.g. epsg3413 ), latlon not working for intersection
    ext_polygons = read_polygons_epsg3413(ext_shp)

    obj_polygons_2d = [read_polygons_epsg3413(item) for item in image_object_paths]

    idx_list = [idx for idx, polys in enumerate(obj_polygons_2d) if b_anyone_within_extents(polys,ext_polygons)]
    print('find %d images within extent'%len(idx_list))
    return idx_list


def save_image_names_to_json(user_name, save_image_names, ext_shp):
    save_dir = os.path.join(BASE_DIR,'data','user_tasks')
    if os.path.isdir(save_dir) is False:
        os.mkdir(save_dir)
    save_file = os.path.join(save_dir,'%s.json'%user_name)

    save_dict = {'user':user_name, 'task_extent': ext_shp,'image_names':save_image_names}

    # ,indent=2 makes the output more readable
    json_data = json.dumps(save_dict,indent=2)
    with open(save_file, "w") as f_obj:
        f_obj.write(json_data)
        print('saved to %s'%save_file)


def main(options, args):
    ext_shp = args[0]
    user_name = options.user_name if options.user_name is not None else 'user'

    # get images in data
    image_names, image_paths, image_Bounds, image_object_paths = read_image_list()

    # change to absolute path
    image_object_paths = [ os.path.join(BASE_DIR,item) for item in image_object_paths]

    # get idx whose images are within extent
    idx_list = get_index_within_extent(ext_shp,image_object_paths)

    # save image names to a json
    save_image_names = [ image_names[item] for item in idx_list ]

    save_image_names_to_json(user_name, save_image_names, ext_shp)


if __name__ == '__main__':
    usage = "usage: %prog [options] ext_shp"
    parser = OptionParser(usage=usage, version="1.0 2022-09-28")
    parser.description = 'Introduction: get a list of image name within an extent'

    parser.add_option("-u", "--user_name",
                      action="store", dest="user_name",
                      help="the user who are going to handle these images")


    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 1:
        parser.print_help()
        sys.exit(2)

    main(options, args)
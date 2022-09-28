#!/bin/bash

# run after enabling the Django environment
ext_shp=~/Data/Arctic/alaska/alaska_extent_shp/alaska_extend_simple.shp
user=lingcao.huang@colorado.edu

./image_names_inExent.py ${ext_shp} -u ${user}
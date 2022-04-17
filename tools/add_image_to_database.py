import os,sys

import sqlite3

from pathlib import Path
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR.absolute()))

# from imageObjects.models import Image    ## need setting of INSTALLED_APPS
from tools.vectorData_io import get_centroid_imagebound_latlon

def insert_one_image_record(cursor,image_name,image_path,image_bound_path, image_object_path, cen_lat, cen_lon):
    # Preparing SQL queries to INSERT a record into the database.
    sql_str = 'INSERT INTO IMAGEOBJECTS_IMAGE(IMAGE_NAME, IMAGE_PATH, IMAGE_BOUND_PATH, IMAGE_OBJECT_PATH, CONCURRENT_COUNT , IMAGE_VALID_TIMES ,IMAGE_CEN_LAT, IMAGE_CEN_LON) VALUES ' \
              '("%s", "%s","%s", "%s", 0, 0, "%f", "%f")'%(image_name,image_path, image_bound_path, image_object_path,cen_lat, cen_lon)
    print(sql_str)
    cursor.execute(sql_str)

def insert_one_image_record_django(image_name,image_path,image_bound_path, image_object_path):
    img = Image(image_name=image_name,image_path=image_path,image_bound_path=image_bound_path,
                image_object_path=image_object_path,concurrent_count=0,image_valid_times=0)
    print(img.id, img.image_name)
    img.save()

def read_image_list():
    img_list_txt = os.path.join(BASE_DIR,'data','imageList.txt')
    if os.path.isfile(img_list_txt) is False:
        raise IOError('%s not exists'%img_list_txt)
    with open(img_list_txt,'r') as f_obj:
        lines = f_obj.readlines()
        image_names = [item.strip() for item in lines]

    image_paths = []
    image_object_paths = []
    image_Bound = []
    for item in image_names:
        image_paths.append(os.path.join(BASE_DIR,'data','images',item+'.png'))
        image_object_paths.append(os.path.join(BASE_DIR,'data','objectPolygons',item+'.geojson'))
        image_Bound.append(os.path.join(BASE_DIR,'data','imageBound',item+'.geojson'))

    return image_names,image_paths,image_Bound,image_object_paths

def test_insert_one_image_record_django():

    # need to set django environment (not sure how), like what in manage.py
    # django.core.exceptions.ImproperlyConfigured: Requested setting INSTALLED_APPS, but settings are not configured.
    # You must either define the environment variable DJANGO_SETTINGS_MODULE or call settings.configure() before accessing settings.
    image_name = 'example_111'
    image_path = 'example.png'
    image_bound_path = 'example_bound.geojson'
    image_object_path = 'example_objects.geojson'
    insert_one_image_record_django(image_name, image_path, image_bound_path, image_object_path)

def main():

    # get images in data
    image_names, image_paths, image_Bounds, image_object_paths = read_image_list()
    # print(image_names, image_paths, image_Bound, image_object_paths)

    # Connecting to sqlite
    conn = sqlite3.connect(os.path.join(BASE_DIR,'db.sqlite3'))

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    for image_name,image_path, image_bound, image_object_path in zip(image_names,image_paths,image_Bounds,image_object_paths):
        center = get_centroid_imagebound_latlon(image_bound)
        cen_lat, cen_lon = center.y, center.x
        insert_one_image_record(cursor, image_name, image_path, image_bound,image_object_path,cen_lat, cen_lon)

    # Commit your changes in the database
    conn.commit()
    print("Image Records inserted........")

    # Closing the connection
    conn.close()

if __name__ == '__main__':
    main()
    # test_insert_one_image_record_django()

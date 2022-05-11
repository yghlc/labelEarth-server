#!/bin/bash

# remove all records in image and userinput
# then insert images from "data" folder

cd ..

# backup data if not exist
if [ ! -f imageObjects.json ]; then
  echo "imageObjects.json does not exist, will create a backup"
  python manage.py dumpdata imageObjects --indent 2 > imageObjects.json
fi

# clear record in tables: image and userinput
python manage.py migrate imageObjects zero    # remove the table
python manage.py migrate imageObjects         # create a empty table

# insert images in "data" to the image table
python ./tools/add_image_to_database.py

#!/bin/bash

# run after enabling the Django environment

cd ..

# tables from json to xlsx: user, image, userinput
python ./tools/export_tables.py auth.user
python ./tools/export_tables.py imageObjects.image
python ./tools/export_tables.py imageObjects.userinput

python ./tools/input_statistics.py
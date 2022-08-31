#!/bin/bash

# run after enabling the Django environment
# ref: https://coderwall.com/p/mvsoyg/django-dumpdata-and-loaddata

cd ..
# backup all data
python manage.py dumpdata --indent 2 > labelEarthServer_db.json

# back up data of admin app
python manage.py dumpdata admin --indent 2 > admin.json

# back up user table
python manage.py dumpdata auth.user --indent 2 > user.json

# back up data of imageObjects
python manage.py dumpdata imageObjects --indent 2 > imageObjects.json

python manage.py dumpdata imageObjects.image --indent 2 > image.json
python manage.py dumpdata imageObjects.userinput --indent 2 > userinput.json

# copy backup files
python ./tools/backdata.py

#!/bin/bash

ls
cd ./main
ls
rm -r migrations
cd ..
ls
cd ./cof
ls
rm db.sqlite3
ls
python manage.py populate
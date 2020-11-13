#!/bin/bash

ls
echo "------------"
cd ./main
ls
echo "------------"
rm -r migrations
cd ..
echo "------------"
cd ./cof
ls
echo "------------"
rm db.sqlite3
ls
echo "------------"
python manage.py testdata
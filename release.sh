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
cd ..
#python manage.py testdata
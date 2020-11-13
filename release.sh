#!/bin/bash

ls
rm -r main/migrations
rm cof/db.sqlite3
ls
python manage.py populate
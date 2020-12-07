# Covid-on-Flight

Keeping airline employees and travelers safer through data

## Introduction

By connecting flights to users and users to COVID-19 statuses, Covid on Flight is able to track potential COVID-19 infections due to airline travel.
Granting passengers awareness of possible exposure through phone and email allows them to take proper steps to protect those around them.
Status reminder updates and infection alerts facilitate Covid on Flight in this manner.
This GitHub repository is the Back-End side to Covid-on-Flight-FE.

## Setup Instructions

The setup assumes the user is working in Ubuntu and has Python 3 installed.

#### Create your virtual environment (if needed)

`python3 -m venv /path/to/newenv`

#### Activate your virtual environment

`source /path/to/newenv/bin/activate`

#### Download and install necessary Python modules

`pip3 install Django`

`pip3 install django_heroku`

`pip3 install django-cors-headers`

`pip3 install twilio`

`pip3 install sendgrid`

#### Populate the database with test data (if desired)

Delete db.sqlite3 file (in cof folder) and migrations folder (in main folder) if necessary.

`python3 manage.py populate`

#### Add a Django administrator account

This grants access to Django's /admin URL that contains database information.

`python3 manage.py createsuperuser`

Follow the prompts as directed.

#### Run Covid on Flight's web server

`python3 manage.py runserver`

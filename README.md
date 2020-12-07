# Covid-on-Flight

Keeping airline employees and travelers safer through data

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

#### Run Covid on Flight's web server

Delete db.sqlite3 file (in cof folder) and migrations folder (in main folder) if necessary.

`python3 manage.py populate`

`python3 manage.py runserver`

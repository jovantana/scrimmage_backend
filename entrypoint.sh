#!/bin/bash

sleep 5
pipenv run flask db upgrade

if [ "$FLASK_ENV" == "development" ]
then    
    pipenv run flask run --host=0.0.0.0    
else # production
    pipenv run gunicorn --worker-class eventlet -w 1 wsgi:app --bind 0.0.0.0:5000
fi

##!/bin/bash
#
## Create a Python 3.8 virtual environment
#python3.8 -m venv venv3.8
#
## Activate the virtual environment
#source venv3.8/bin/activate
#
## Install dependencies from requirements.txt
#pip install -r requirements.txt
#
## Run Django migrations
#python manage.py migrate
#
## Start the Django development server
#python manage.py runserver
#
## To keep the script running after starting the server, if necessary
#exec "$SHELL"

#!/bin/bash

set -e

# Create a Python 3.8 virtual environment
echo "Creating Python 3.8 virtual environment..."
python3.8 -m venv venv3.8

# Activate the virtual environment and install dependencies
echo "Activating virtual environment and installing dependencies..."
source venv3.8/bin/activate
pip install -r requirements.txt

# Run Django migrations
echo "Running Django migrations..."
python manage.py migrate

# Start Django development server
echo "Starting Django development server..."
python manage.py runserver

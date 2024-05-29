#!/bin/bash

echo "Building project package..."
pip install -r requirements.txt

echo "Building migartion..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput


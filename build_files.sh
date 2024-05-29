#!/bin/bash

echo "Building project package..."
python3 -m pip install -r requirements.txt

echo "Building migartion..."
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput


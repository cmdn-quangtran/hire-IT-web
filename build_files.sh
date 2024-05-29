#!/bin/bash

echo "Building project package..."
pip3 install -r requirements.txt

echo "Building migartion..."
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput


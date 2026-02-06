#!/bin/bash

# Set library path for Pillow to find libtiff
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH

# Start Django development server on port 8000
python manage.py runserver 8011

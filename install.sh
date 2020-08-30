#!/bin/bash
set -ex
cp bootstrap.min.css \
   bootstrap.min.js \
   jquery-3.5.1.min.js \
   popper.min.js \
   vue.js \
   "$1"/
cp kooking.html "$1"/index.html

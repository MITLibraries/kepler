#!/bin/sh
set -e

if [ ! -d "$HOME/gdal/lib" ]; then
  wget http://download.osgeo.org/gdal/1.11.1/gdal-1.11.1.tar.gz
  tar -xzf gdal-1.11.1.tar.gz
  cd gdal-1.11.1 && ./configure --prefix=$HOME/gdal && make && make install
else
  echo "Using cached directory."
fi

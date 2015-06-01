.. kepler documentation master file, created by
   sphinx-quickstart on Tue Apr 28 10:05:23 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Kepler's documentation!
==================================

Kepler automates several aspects of the GIS data workflow process.


Installation
------------

Kepler relies on GDAL to perform a few necessary steps in processing GeoTIFFs. You will need to make sure you have the ``libgdal``, ``libgdal-dev`` and ``gdal-bin`` packages installed on your system before installing the python dependencies. The version of the system GDAL should match the version of the python bindings specified in the ``requirements.txt`` file. Make a note of where the header files have been installed. This should usually be ``/usr/include/gdal``, but you can check with::

    $ gdal-config --cflags

Then, from the project root::

    $ env CPLUS_INCLUDE_PATH=/usr/include/gdal \
    > C_INCLUDE_PATH=/usr/include/gdal \
    > pip install -r requirements.txt

Replace ``/usr/include/gdal`` with wherever the header files are on your system.


Running the Tests
-----------------

You should have python binaries for 2.6, 2.7, 3.3 and 3.4 available on your system. Install `tox <https://tox.readthedocs.org/en/latest/>`_ and run::

    $ tox


Building the Documentation
--------------------------

Make sure `Sphinx <http://sphinx-doc.org/latest/index.html>`_ is installed. Then::

    $ cd docs
    $ make html


Contents:

.. toctree::
   :maxdepth: 2

   metadata
   application

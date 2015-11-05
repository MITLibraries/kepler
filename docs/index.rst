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


Configuration
-------------

Kepler uses environment variables to manage application configuration. These should be placed in a ``.env`` file at the root of the project. The following variables should be set:

+------------------------------+---------------------------------------+
| ``SQLALCHEMY_DATABASE_URI``  | Location of sqlite database           |
+------------------------------+---------------------------------------+
| ``GEOSERVER_PUBLIC_URL``     | URL for public GeoServer instance     |
+------------------------------+---------------------------------------+
| ``GEOSERVER_RESTRICTED_URL`` | URL for secure GeoServer instance     |
+------------------------------+---------------------------------------+
| ``GEOSERVER_WORKSPACE``      | Name of workspace for data            |
+------------------------------+---------------------------------------+
| ``GEOSERVER_DATASTORE``      | Name of datastore for shapefiles      |
+------------------------------+---------------------------------------+
| ``SOLR_URL``                 | URL for GeoBlacklight Solr instance   |
+------------------------------+---------------------------------------+
| ``SWORD_SERVICE_URL``        | URL for DSpace SWORD service          |
+------------------------------+---------------------------------------+
| ``SWORD_SERVICE_USERNAME``   | Username for SWORD service            |
+------------------------------+---------------------------------------+
| ``SWORD_SERVICE_PASSWORD``   | Password for SWORD service            |
+------------------------------+---------------------------------------+
| ``UUID_NAMESPACE``           | The namespace used in generating the  |
|                              | version 5 UUID                        |
+------------------------------+---------------------------------------+
| ``SECRET_KEY``               | Randomly generated key                |
+------------------------------+---------------------------------------+
| ``OAI_ORE_URL``              | URL for OAI ORE DSpace service        |
+------------------------------+---------------------------------------+
| ``GEOSERVER_AUTH_USER``      | Username for GeoServer REST service   |
+------------------------------+---------------------------------------+
| ``GEOSERVER_AUTH_PASS``      | Password for GeoServer REST service   |
+------------------------------+---------------------------------------+


Running the Application Locally
-------------------------------

The application can be run locally using either the heroku toolbelt or honcho. For example, from project root::

    $ honcho start


Running the Tests
-----------------

You should have python binaries for 2.7, 3.3 and 3.4 available on your system. Install `tox <https://tox.readthedocs.org/en/latest/>`_ and run::

    $ tox


Building the Documentation
--------------------------

In order to generate the documentation you have to make sure `Sphinx <http://sphinx-doc.org/latest/index.html>`_ is installed in a virtualenv `along with all the kepler dependencies`. One possibility is to create a different virtualenv for generating the docs. For example::

    $ cd /path/to/kepler
    $ mkvirtualenv kepler-docs
    (kepler-docs)$ pip install Sphinx
    (kepler-docs)$ env CPLUS_INCLUDE_PATH=/usr/local/include \
        C_INCLUDE_PATH=/usr/local/include pip install -r requirements.txt
    (kepler-docs)$ cd docs
    (kepler-docs)$ make html

This will place the built documents in ``kepler/docs/_build/``.


Documentation Contents
----------------------

.. toctree::
   :maxdepth: 2

   metadata
   application

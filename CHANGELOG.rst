Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


[0.2.1] - 2024-04-03
--------------------

Fixed
~~~~~~~

* TypeError: GEOSGeometry.__init__() got an unexpected keyword argument 'geom_input'


[0.2.0] - 2024-04-03
--------------------

Changed
~~~~~~~

* renamed package from `django-axis-order` to `django-epsg-cache`

Added
~~~~~

* fetches extent of the crs from the epsg api and provide it with the `SpatialReference` object.


[0.1.1] - 2023-12-04
--------------------

Changed
~~~~~~~

* remove the django and requests maximum version restriction inside setup.py


[0.1.0] - 2023-05-04
--------------------

Added
~~~~~

* Registry cache, which fetches the epsg wkt and cache it inside the defined django cache
* several utility functions to switch/adjust the axis order
* custom SpatialReference model which extends the gdal SpatialReference object to discover the axis order with gdal help
            

[unreleased]: https://github.com/mrmap-community/django-epsg-cache/compare/v0.1.0...HEAD
[0.0.1]: https://github.com/mrmap-community/django-epsg-cache/releases/tag/v0.1.0
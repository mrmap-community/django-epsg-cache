Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
            

[unreleased]: https://github.com/mrmap-community/django-axis-order/compare/v0.1.0...HEAD
[0.0.1]: https://github.com/mrmap-community/django-axis-order/releases/tag/v0.1.0
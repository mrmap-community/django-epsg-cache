.. _tutorial:


Tutorial
========

In this tutorial you will learn about how to use the `django-epsg-cache` package which implements a local cache of the `epsg registry <https://epsg.org/API_UsersGuide.html>`_ with fallback to gdal.


Usage with ogc service
----------------------

In geo applications `coordinate tuples <https://wiki.osgeo.org/wiki/Axis_Order_Confusion>`_ can be ordered either (x,y) or (y,x) or (x,y) but meant as (y,x). 
For example, in some `ogc service versions <https://docs.geoserver.org/2.23.x/en/user/services/wfs/axis_order.html>`_, the axis order interpretation was changed.
So if a request comes in, you need to initialize your geometry objects with correct axis order.

In newer ogc standards, the axis order from the registered epsg reference system shall be used. 
That is the main problem we gona fix here. We fetch the wkt description from the remote epsg resgistry api and transform the geometry to the correct axis order if needed:

.. code-block:: python

    from epsg_cache.utils import adjust_axis_order

    correct_geometry = adjust_axis_order(geometry)


.. warning:: 

    You need to decide by your self, for what service version you need a axis order correction.

from ctypes import c_void_p

from django.contrib.gis.gdal import SpatialReference as GdalSpatialReference
from django.contrib.gis.gdal.libgdal import lgdal
from django.contrib.gis.gdal.prototypes.generation import int_output
from django.contrib.gis.geos import GEOSGeometry

# see c++ api ref: https://gdal.org/api/ogrspatialref.html
get_epsg_treats_as_lat_long = int_output(
    lgdal.OSREPSGTreatsAsLatLong, [c_void_p])
get_epsg_treats_as_northing_easting = int_output(
    lgdal.OSREPSGTreatsAsNorthingEasting, [c_void_p])


class Origin(enumerate):
    """Enum to declarative different origins"""
    CACHE = "from_cache"
    LOCAL_GDAL = "from_local_gdal"
    EPSG_REGISTRY = "from_remote_registry"


class EPSGExtent(GEOSGeometry):
    extent_id: int = None

    def __init__(self, extent_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.extent_id = extent_id

    def __eq__(self, other: object):
        return super().__eq__(other) and self.extent_id == other.extent_id


class SpatialReference(GdalSpatialReference):
    """Class to extend the :class:`django.contrib.gis.gdal.SpatialReference` class by additional attributes and
    properties.

    Implement the c gdal lib function calls for OSREPSGTreatsAsLatLong and OSREPSGTreatsAsNorthingEasting to get the
    axis order interpretation. See https://wiki.osgeo.org/wiki/Axis_Order_Confusion for detail problem.

    :param origin: the origin of this ``SpatialReference`` instance. Used in
                   :class:`epsg_cache.registry.Registry` to signal where the information for this instance
                   comes from.
    :type origin: :class:`~Origin`
    """
    _extent: EPSGExtent = None

    def __init__(self, origin: Origin = Origin.CACHE, extent: EPSGExtent = None, *args, **kwargs):
        """Custom init function to store origin."""
        self.origin = origin
        self._extent = extent
        super().__init__(*args, **kwargs)

    def __epsg_treats_as_lat_long(self):
        return bool(get_epsg_treats_as_lat_long(self.ptr))

    def __epsg_treats_as_northing_easting(self):
        return bool(get_epsg_treats_as_northing_easting(self.ptr))

    @property
    def is_yx_order(self) -> bool:
        """Return True if the axis order is lat,lon | north, east"""
        if self.geographic:
            return self.__epsg_treats_as_lat_long()
        elif self.projected:
            return self.__epsg_treats_as_northing_easting()

    @property
    def is_xy_order(self) -> bool:
        """Return True if the axis order is lon,lat | east, north"""
        return not self.is_yx_order

    def __eq__(self, other: object) -> bool:
        return self.srid == other.srid and self.origin == other.origin

    @property
    def extent(self) -> EPSGExtent:
        return self._extent

    @extent.setter
    def extent(self, geom: EPSGExtent):
        self._extent = geom

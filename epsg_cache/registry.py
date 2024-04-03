from django.core.cache import caches
from django.utils.connection import ConnectionProxy
from lxml import etree
from requests import Request, Session

from epsg_cache.models import EPSGExtent, Origin, SpatialReference
from epsg_cache.settings import (CACHE_BACKEND, EPSG_API_URL, KEY_PREFIX, TTL,
                                 TTL_FALLBACK)


class Registry(object):
    """Cached Epsg Registry based on django cache framework.

    Cause reference systems from the epsg namespace are dynamic (see [CIT_EPSG]_) we need to fetch them from the remote
    EPSG API (https://apps.epsg.org/api/swagger/ui/index).

    .. [CIT_EPSG] The EPSG Registry has migrated from a previous platform. The data model on this new site has been
       upgraded to follow the ISO 19111:2019 revisions for dynamic datums, geoid-based vertical datums, datum ensembles
       and derived projected coordinate reference systems. (from https://epsg.org/home.html)

    To get the :class:`epsg_cache.models.SpatialReference` objects the workflow described in
    :meth:`epsg_cache.registry.Registry.get`` is used.

    :Example:

    >>> from epsg_cache import Registry

    >>> registry = Registry()
    >>> sr = registry.get(srid=4326)

    >>> print(sr.is_xy_order())
    >>> True
    """

    epsg_api_url = EPSG_API_URL
    cache_prefix = KEY_PREFIX
    ttl = TTL
    fallback_ttl = TTL_FALLBACK
    cache = ConnectionProxy(caches, CACHE_BACKEND)

    def __init__(self, proxies=None):
        self.proxies = proxies

    def _get_session(self):
        s = Session()
        if self.proxies:
            s.proxies = self.proxies
        return s

    def _fetch(self, request: Request):
        s = self._get_session()
        return s.send(request=request.prepare())

    def _fetch_extend(self, eid: int) -> EPSGExtent:
        try:
            request = Request(
                method="GET",
                url=f"{self.epsg_api_url}Extent/{eid}/polygon/",
            )
            response = self._fetch(request=request)
            if response.status_code < 300:
                return response.content
        except ConnectionError:
            pass

    def _fetch_coord_ref_system(self, srid: int, format: str = "wkt") -> str:
        """Fetch the wkt for a given srid from remote epsg api

        :return: the spatial reference
        :rtype: :class:`epsg_cache.models.SpatialReference`
        """
        try:
            request = Request(
                method="GET",
                url=f"{self.epsg_api_url}CoordRefSystem/{srid}/export/",
                params={"format": format})
            response = self._fetch(request=request)
            if response.status_code < 300:
                return response.content
        except ConnectionError:
            pass
        return ""

    def _get_extent(self, eid: int):
        geojson = self._fetch_extend(eid=eid)
        if geojson:
            try:
                return EPSGExtent(extent_id=eid, geo_input=geojson)
            except Exception:
                pass

    def _get_extent_id(self, srid: int):
        gml = self._fetch_coord_ref_system(srid=srid, format="gml")
        if gml:
            ns = {
                "epsg": "urn:x-ogp:spec:schema-xsd:EPSG:2.3:dataset",
                "gml": "http://www.opengis.net/gml/3.2",
                "xlink": "http://www.w3.org/1999/xlink"
            }
            try:
                if isinstance(gml, str):
                    gml = gml.encode()
                root = etree.fromstring(gml)
                extent_url = root.xpath(
                    './/gml:metaDataProperty/epsg:CommonMetaData/epsg:Usage/epsg:extent/@xlink:href', namespaces=ns)
                if extent_url and isinstance(extent_url, list):
                    extent_url = extent_url[0]
                extent_id = extent_url.split('/Extent/')[1].split('/export')[0]
                return int(extent_id)
            except Exception:
                pass

    def get_extent(self, srid: int) -> EPSGExtent:
        extent = None
        extent_id = self._get_extent_id(srid=srid)
        if extent_id:
            extent = self._get_extent(eid=extent_id)
        return extent

    def get_spatial_reference_system(self, srid: int) -> SpatialReference:
        wkt = self._fetch_coord_ref_system(srid=srid)
        if wkt:
            return SpatialReference(
                origin=Origin.EPSG_REGISTRY,
                srs_input=wkt,
                srs_type="wkt",
                extent=self.get_extent(srid=srid)
            )

    def get(self, srid: int) -> SpatialReference:
        """Return the SpatialReference object by given srid from three different origins.
        1th: cache is uses to lookup a cached spatial reference
        2th: remote epsg api is fetched to lookup the remote spatial reference
        3th: fallback to the local gdal registry

        :return: the initialized spatial reference object with the origin information.
        :rtype: :class:`epsg_cache.models.SpatialReference`

        """
        cached_crs = self.cache.get(
            key=f"{self.cache_prefix}-crs-{srid}", version=Origin.EPSG_REGISTRY)
        if not cached_crs:
            crs = self.get_spatial_reference_system(srid=srid)
            if crs:
                self.set(srid=srid, crs=crs)
            else:
                crs = SpatialReference(
                    origin=Origin.LOCAL_GDAL,
                    srs_input=srid,
                    extent=self.get_extent(srid=srid)
                )
            return crs
        else:
            crs_input, extent_id, extent_input = cached_crs.split(";")

            if extent_input:
                extent = EPSGExtent(
                    extent_id=extent_id,
                    geom_input=extent_input)
            else:
                extent = self.get_extent(srid=srid)

            return SpatialReference(
                srs_input=crs_input,
                srs_type="wkt",
                extent=extent
            )

    def set(self, srid: int, crs: SpatialReference) -> None:
        """Store the wkt of the given crs"""
        self.cache.set(
            key=f"{self.cache_prefix}-crs-{srid}",
            value=f"{crs.wkt};{crs.extent.extent_id if crs.extent else ''};{crs.extent.wkt if crs.extent else ''}",
            timeout=self.ttl if crs.origin == Origin.EPSG_REGISTRY else self.fallback_ttl,
            version=Origin.EPSG_REGISTRY
        )

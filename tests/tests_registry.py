from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from requests import Request
from requests.sessions import Session

from axis_order_cache.models import Origin, SpatialReference
from axis_order_cache.registry import Registry

WKT_4326 = 'GEOGCRS["WGS 84",ENSEMBLE["World Geodetic System 1984 ensemble", MEMBER["World Geodetic System 1984 (Transit)", ID["EPSG",1166]], MEMBER["World Geodetic System 1984 (G730)", ID["EPSG",1152]], MEMBER["World Geodetic System 1984 (G873)", ID["EPSG",1153]], MEMBER["World Geodetic System 1984 (G1150)", ID["EPSG",1154]], MEMBER["World Geodetic System 1984 (G1674)", ID["EPSG",1155]], MEMBER["World Geodetic System 1984 (G1762)", ID["EPSG",1156]], MEMBER["World Geodetic System 1984 (G2139)", ID["EPSG",1309]], ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1,ID["EPSG",9001]],ID["EPSG",7030]], ENSEMBLEACCURACY[2],ID["EPSG",6326]],CS[ellipsoidal,2,ID["EPSG",6422]],AXIS["Geodetic latitude (Lat)",north],AXIS["Geodetic longitude (Lon)",east],ANGLEUNIT["degree",0.0174532925199433,ID["EPSG",9102]],ID["EPSG",4326]]'
WKT_4647 = 'PROJCRS["ETRS89 / UTM zone 32N (zE-N)",BASEGEOGCRS["ETRS89",ENSEMBLE["European Terrestrial Reference System 1989 ensemble", MEMBER["European Terrestrial Reference Frame 1989", ID["EPSG",1178]], MEMBER["European Terrestrial Reference Frame 1990", ID["EPSG",1179]], MEMBER["European Terrestrial Reference Frame 1991", ID["EPSG",1180]], MEMBER["European Terrestrial Reference Frame 1992", ID["EPSG",1181]], MEMBER["European Terrestrial Reference Frame 1993", ID["EPSG",1182]], MEMBER["European Terrestrial Reference Frame 1994", ID["EPSG",1183]], MEMBER["European Terrestrial Reference Frame 1996", ID["EPSG",1184]], MEMBER["European Terrestrial Reference Frame 1997", ID["EPSG",1185]], MEMBER["European Terrestrial Reference Frame 2000", ID["EPSG",1186]], MEMBER["European Terrestrial Reference Frame 2005", ID["EPSG",1204]], MEMBER["European Terrestrial Reference Frame 2014", ID["EPSG",1206]], ELLIPSOID["GRS 1980",6378137,298.257222101,LENGTHUNIT["metre",1,ID["EPSG",9001]],ID["EPSG",7019]], ENSEMBLEACCURACY[0.1],ID["EPSG",6258]],ID["EPSG",4258]],CONVERSION["UTM zone 32N with prefix",METHOD["Transverse Mercator",ID["EPSG",9807]],PARAMETER["Latitude of natural origin",0,ANGLEUNIT["degree",0.0174532925199433,ID["EPSG",9102]],ID["EPSG",8801]],PARAMETER["Longitude of natural origin",9,ANGLEUNIT["degree",0.0174532925199433,ID["EPSG",9102]],ID["EPSG",8802]],PARAMETER["Scale factor at natural origin",0.9996,SCALEUNIT["unity",1,ID["EPSG",9201]],ID["EPSG",8805]],PARAMETER["False easting",32500000,LENGTHUNIT["metre",1,ID["EPSG",9001]],ID["EPSG",8806]],PARAMETER["False northing",0,LENGTHUNIT["metre",1,ID["EPSG",9001]],ID["EPSG",8807]],ID["EPSG",4648]],CS[Cartesian,2,ID["EPSG",4400]],AXIS["Easting (E)",east],AXIS["Northing (N)",north],LENGTHUNIT["metre",1,ID["EPSG",9001]],ID["EPSG",4647]]'


class MockResponse:

    def __init__(self, status_code=200, content=None):
        self.status_code = status_code
        self.content = content


request_counter = 1


def side_effect(request: Request):
    global request_counter
    request_counter += 1
    if "4326" in request.url:
        return MockResponse(status_code=200, content=WKT_4326)
    else:
        return MockResponse(status_code=400)


class TestUtils(TestCase):

    def setUp(self):
        self.registry = Registry()

    def tearDown(self):
        cache.clear()
        global request_counter
        request_counter = 0

    @patch.object(Session, 'send', side_effect=side_effect)
    def test_get_from_api(self, mock_response):
        result = self.registry.get(srid=4326)

        expected = SpatialReference(
            origin=Origin.EPSG_REGISTRY, srs_input=WKT_4326, srs_type="wkt")

        self.assertEqual(expected, result)
        self.assertEqual(1, request_counter)
        print(request_counter)

    @patch.object(Session, 'send', side_effect=side_effect)
    def test_get_from_local_gdal(self, mock_response):
        result = self.registry.get(srid=4647)

        expected = SpatialReference(
            origin=Origin.LOCAL_GDAL, srs_input=WKT_4647, srs_type="wkt"
        )
        self.assertEqual(expected, result)
        self.assertEqual(1, request_counter)
        print(request_counter)

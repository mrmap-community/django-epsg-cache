from django.contrib.gis.gdal.geometries import MultiPolygon as GdalMultiPolygon
from django.contrib.gis.gdal.geometries import Point as GdalPoint
from django.contrib.gis.gdal.geometries import Polygon as GdalPolygon
from django.contrib.gis.geos import MultiPolygon, Point, Polygon
from django.test import TestCase

from axis_order_cache.utils import switch_axis_order


class TestUtils(TestCase):

    def setUp(self):
        self.polygon = "SRID=4326;POLYGON((0 1,0 50,51 50,50 0,0 1))"
        self.polygon_expected = "SRID=4326;POLYGON((1 0,50 0,50 51,0 50,1 0))"

    def test_switch_axis_order_with_geos_polygon(self):
        polygon = Polygon.from_ewkt(self.polygon)
        expected = Polygon.from_ewkt(self.polygon_expected)
        result = switch_axis_order(geometry=polygon)

        self.assertEqual(expected, result)

    def test_switch_axis_order_with_gdal_polygon(self):
        polygon = GdalPolygon(self.polygon)
        expected = GdalPolygon(self.polygon_expected)
        result = switch_axis_order(geometry=polygon)

        self.assertEqual(expected, result)

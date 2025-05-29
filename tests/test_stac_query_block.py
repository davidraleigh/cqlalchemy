import json
import unittest
import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
import shapely
from shapely import Point

from cqlalchemy.stac.query import (
    Framework,
    ObservationDirection,
    QueryBuilder,
    _NumberQuery,
)

GEOMETRY_ERRORS = [
    ('MultiPolygon', [[[[0, 3], [0, 4], [0, 5]]]], shapely.errors.GEOSException),
    ('MultiPolygon', [[[[0, 3], [0, 4], [0, 5], [0, 3]]]], False),
    ('MultiPolygon', [[[[0, 3, 4], [0, 4, 4], [0, 5, 4], [0, 3, 2]]]], False),
    ('MultiPolygon', [[[[0, 3, 4, 5], [0, 4, 4, 5], [0, 5, 4, 5], [0, 3, 2, 5]]]], ValueError),
    ('Polygon', [[[0, 3], [0, 4], [0, 5]]], shapely.errors.GEOSException),
    ('Polygon', [[[0, 3], [0, 4], [0, 5], [0, 3]]], False),
    ('Polygon', [[[0, 3, 3], [0, 4, 2], [0, 2,  5], [0, 2, 3]]], False),
    ('Polygon', [[[0, 3, 3, 4], [0, 4, 4, 2], [0, 4, 2, 5], [0, 2, 4, 3]]], ValueError),
    ('LineString', [[0, 3]], shapely.errors.GEOSException),
    ('MultiPoint', [[0, 3]], False),
    ('LineString', [[0, 3], [0, 4]], False),
    ('MultiPoint', [[0, 3], [0, 4]], False),
    ('LineString', [[0, 3, 5], [0, 4, 5]], False),
    ('MultiPoint', [[0, 3, 5], [0, 4, 5]], False),
    ('LineString', [[0, 3, 5, 5], [0, 4, 5, 5]], ValueError),
    ('MultiPoint', [[0, 3, 5, 5], [0, 4, 5, 5]], ValueError),
    ('Point', [0, 3], False),
    ('Point', [0, 3, 4], False),
    ('Point', [0, 3, 4, 3], ValueError),
]


@pytest.mark.parametrize("geometry_type,coordinates,exception", GEOMETRY_ERRORS)
def test_geometry_errors(geometry_type, coordinates, exception):
    a = QueryBuilder()
    geom_dict = {'type': geometry_type, 'coordinates': coordinates}
    if not exception:
        a.geometry.intersects(geom_dict)
    else:
        pytest.raises(exception, a.geometry.intersects, geom_dict)


class STACTestCase(unittest.TestCase):
    def test_datetime(self):
        a = QueryBuilder()
        t = datetime.now(tz=timezone.utc)
        a.datetime.lt(t)
        a_dict = a.query_dump()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "<")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], t)
        a.query_dump_json()

    def test_created(self):
        a = QueryBuilder()
        t = datetime.now(tz=timezone.utc)
        a.created.lte(t)
        a_dict = a.query_dump()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "<=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "created")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], t)
        a.query_dump_json()

    def test_created_overwrite_lt(self):
        a = QueryBuilder()
        t = datetime.now(tz=timezone.utc)
        a.created.lte(t)
        a.created.lt(t)
        a_dict = a.query_dump()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "<")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "created")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], t)
        a.query_dump_json()

    def test_created_overwrite_eq(self):
        a = QueryBuilder()
        t = datetime.now(tz=timezone.utc)
        a.created.lte(t)
        a.query_dump()
        a.created.equals(t)
        a_dict = a.query_dump()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "created")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], t)
        a.query_dump_json()

    def test_updated(self):
        a = QueryBuilder()
        t = datetime.now(tz=timezone.utc)
        a.updated.gte(t)
        a_dict = a.query_dump()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], ">=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "updated")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], t)
        a.query_dump_json()

    def test_equals_date(self):
        a = QueryBuilder()
        d = date(2024, 1, 1)
        a.datetime.equals(d)
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["op"], ">=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][1].year, d.year)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][1].hour, 0)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][1].month, d.month)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][1].day, d.day)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][1].minute, 0)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][1].second, 0)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][1].tzinfo, timezone.utc)

        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["op"], "<=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][1].year, d.year)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][1].hour, 23)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][1].month, d.month)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][1].day, d.day)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][1].minute, 59)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][1].second, 59)
        a.query_dump_json()

    def test_datetime_raises(self):
        a = QueryBuilder()
        d = datetime(2024, 1, 1, 0, 0, 0)
        self.assertRaises(ValueError, a.datetime.equals, d)
        self.assertRaises(ValueError, a.datetime.lt, d)
        self.assertRaises(ValueError, a.datetime.gt, d)
        self.assertRaises(ValueError, a.datetime.gte, d)
        self.assertRaises(ValueError, a.datetime.lte, d)
        a.query_dump_json()

    def test_equals_datetime(self):
        a = QueryBuilder()
        d = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        a.datetime.equals(d)
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1].year, d.year)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1].hour, 0)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1].month, d.month)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1].day, d.day)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1].minute, 0)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1].second, 0)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1].tzinfo, timezone.utc)
        a.query_dump_json()

    def test_platform(self):
        a = QueryBuilder()
        a.platform.equals("Landsat8")
        a_dict = a.query_dump()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "platform")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], "Landsat8")

        a = QueryBuilder()
        a.platform.like("Landsat%")
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "like")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "platform")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], "Landsat%")
        a.query_dump_json()

    def test_platform_overwrite_like(self):
        a = QueryBuilder()
        a.platform.equals("Landsat8")
        a_dict = a.query_dump()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "platform")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], "Landsat8")

        a.platform.like("Landsat%")
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "like")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "platform")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], "Landsat%")
        a.query_dump_json()

    def test_gsd(self):
        a = QueryBuilder()
        a.view.azimuth.gte(0.25)
        a.view.azimuth.lte(0.75)
        a_dict = a.query_dump()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["op"], ">=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][0]["property"], "view:azimuth")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][1], 0.25)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["op"], "<=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][0]["property"], "view:azimuth")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][1], 0.75)
        a.query_dump_json()

    def test_gsd_overwrite_equals(self):
        a = QueryBuilder()
        a.view.azimuth.gte(0.25)
        a.view.azimuth.lte(0.75)
        a_dict = a.query_dump()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["op"], ">=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][0]["property"], "view:azimuth")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][1], 0.25)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["op"], "<=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][0]["property"], "view:azimuth")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][1], 0.75)

        a.view.azimuth.equals(0.5)
        a_dict = a.query_dump()

        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "view:azimuth")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], 0.5)
        a.query_dump_json()

    def test_spatial(self):
        a = QueryBuilder()
        a.geometry.intersects(Point(4, 5))
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "s_intersects")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "geometry")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["type"], "Point")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["coordinates"][0], 4)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["coordinates"][1], 5)

        a.geometry.intersects(Point(4, 5).buffer(1))
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "s_intersects")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "geometry")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["type"], "Polygon")
        a.query_dump_json()

    def test_spatial_dict(self):
        a = QueryBuilder()
        a.geometry.intersects(Point(4, 5).__geo_interface__)
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "s_intersects")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "geometry")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["type"], "Point")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["coordinates"][0], 4)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["coordinates"][1], 5)
        a.query_dump_json()

    def test_spatial_dict_multipolygon(self):
        geom_dict = {'type': 'MultiPolygon', 'coordinates': [[[[-121.2342, 47.7789], [-121.1192, 47.7789],
                                                               [-121.0644, 47.7132], [-121.1301, 47.6748],
                                                               [-121.1137, 47.5981], [-121.1137, 47.5981],
                                                               [-121.2287, 47.5653], [-121.4642, 47.3681],
                                                               [-121.4259, 47.286], [-121.3437, 47.2805],
                                                               [-121.3656, 47.2257], [-121.3108, 47.2038],
                                                               [-121.3054, 47.1381], [-121.4094, 47.1216],
                                                               [-121.382, 47.0888], [-121.7873, 47.1764],
                                                               [-121.9462, 47.1381], [-122.0941, 47.1928],
                                                               [-122.1379, 47.2586], [-122.335, 47.2586],
                                                               [-122.4172, 47.3188], [-122.3241, 47.3462],
                                                               [-122.4227, 47.5762], [-122.3405, 47.5981],
                                                               [-122.4281, 47.6584], [-122.3789, 47.7186],
                                                               [-122.3953, 47.7789], [-121.2342, 47.7789]]], [
                                                                 [[-122.5377, 47.3572], [-122.5377, 47.401],
                                                                  [-122.4829, 47.5105], [-122.4336, 47.4667],
                                                                  [-122.4391, 47.4064], [-122.3734, 47.39],
                                                                  [-122.4939, 47.3298], [-122.5377, 47.3572]]]]}

        shapely.from_geojson(json.dumps(geom_dict))
        a = QueryBuilder()
        a.geometry.intersects(geom_dict)
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "s_intersects")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "geometry")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["type"], "MultiPolygon")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["coordinates"][0][0][0][0], -121.2342)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["coordinates"][0][0][0][1], 47.7789)
        a.query_dump_json()

    def test_bad_geometry_dict(self):
        geom_dict = {'type': 'MultiPolygon', 'coordinates': [[[[-121.2342, 47.7789], [-121.1192, 47.7789],
                                                               [-121.0644, 47.7132], [-121.1301, 47.6748],
                                                               [-121.1137, 47.5981], [-121.1137, 47.5981],
                                                               [-121.2287, 47.5653], [-121.4642, 47.3681],
                                                               [-121.4259, 47.286], [-121.3437, 47.2805],
                                                               [-121.3656, 47.2257], [-121.3108, 47.2038],
                                                               [-121.3054, 47.1381], [-121.4094, 47.1216],
                                                               [-121.382, 47.0888], [-121.7873, 47.1764],
                                                               [-121.9462, 47.1381], [-122.0941, 47.1928],
                                                               [-122.1379, 47.2586], [-122.335, 47.2586],
                                                               [-122.4172, 47.3188], [-122.3241, 47.3462],
                                                               [-122.4227, 47.5762], [-122.3405, 47.5981],
                                                               [-122.4281, 47.6584], [-122.3789, 47.7186]]],
                                                             [[[-122.5377, 47.3572], [-122.5377, 47.401],
                                                               [-122.4829, 47.5105], [-122.4336, 47.4667],
                                                               [-122.4391, 47.4064], [-122.3734, 47.39]]]]}
        a = QueryBuilder()
        pytest.raises(shapely.errors.GEOSException, a.geometry.intersects, geom_dict)

    def test_geojson_string(self):
        a = QueryBuilder()
        pytest.raises(ValueError, a.geometry.intersects, json.dumps(Point(4, 5).__geo_interface__))

    def test_spatial_overwrite_null(self):
        a = QueryBuilder()
        a.geometry.is_null()
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "isNull")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "geometry")
        self.assertEqual(1, len(a_dict["filter"]["args"][0]["args"][0]))

        a.geometry.intersects(Point(4, 5))
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "s_intersects")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "geometry")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["type"], "Point")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["coordinates"][0], 4)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["coordinates"][1], 5)
        a.query_dump_json()

    def test_top_level_is_or(self):
        a = QueryBuilder()
        updated = datetime.now(tz=timezone.utc)
        created = datetime.now(tz=timezone.utc)
        a.updated.gte(updated)
        a.created.lte(created)
        a_dict = a.query_dump(top_level_is_or=True)

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "or")
        self.assertEqual(a_dict["filter"]["args"][1]["op"], ">=")
        self.assertEqual(a_dict["filter"]["args"][1]["args"][0]["property"], "updated")
        self.assertEqual(a_dict["filter"]["args"][1]["args"][1], updated)
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "<=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "created")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], created)
        a.query_dump_json()

    def test_datetime_range_and(self):
        start = datetime.now(tz=timezone.utc)
        end = start + timedelta(days=1)
        a = QueryBuilder()
        a.datetime.gt(start).datetime.lt(end)
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["op"], ">")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][1], start)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["op"], "<")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][1], end)
        a.query_dump_json()

    def test_datetime_range_and_overwrite(self):
        start = datetime.now(tz=timezone.utc)
        end = start + timedelta(days=1)
        a = QueryBuilder()
        a.datetime.gt(start).datetime.lt(end)
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["op"], ">")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][1], start)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["op"], "<")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][1], end)

        a.datetime.equals(start.date(), tzinfo=timezone.utc)
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["op"], ">=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][1], datetime(start.year, start.month, start.day, 0, 0, 0, tzinfo=timezone.utc))
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["op"], "<=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][1], datetime(start.year, start.month,
                                                                                     start.day, 23, 59,
                                                                                     59, 999999,
                                                                                     tzinfo=timezone.utc))
        a.query_dump_json()

    def test_datetime_range_or(self):
        start = datetime.now(tz=timezone.utc)
        end = start + timedelta(days=1)
        a = QueryBuilder()
        a.datetime.gt(end).datetime.lt(start)
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "or")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["op"], "<")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][1], start)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["op"], ">")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][1], end)
        a.query_dump_json()

    def test_extension_eo(self):
        a = QueryBuilder()
        t = datetime.now(tz=timezone.utc)
        a.datetime.lt(t).sar.resolution_azimuth.lt(45).created.gt(t)
        a_dict = a.query_dump()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "<")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], t)
        self.assertEqual(a_dict["filter"]["args"][1]["op"], ">")
        self.assertEqual(a_dict["filter"]["args"][1]["args"][0]["property"], "created")
        self.assertEqual(a_dict["filter"]["args"][1]["args"][1], t)
        self.assertEqual(a_dict["filter"]["args"][2]["op"], "<")
        self.assertEqual(a_dict["filter"]["args"][2]["args"][0]["property"], "sar:resolution_azimuth")
        self.assertEqual(a_dict["filter"]["args"][2]["args"][1], 45)

        a.sar.resolution_azimuth.gt(10)
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter"]["args"][2]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][2]["args"][0]["op"], ">")
        self.assertEqual(a_dict["filter"]["args"][2]["args"][0]["args"][0]["property"], "sar:resolution_azimuth")
        self.assertEqual(a_dict["filter"]["args"][2]["args"][0]["args"][1], 10)
        self.assertEqual(a_dict["filter"]["args"][2]["args"][1]["op"], "<")
        self.assertEqual(a_dict["filter"]["args"][2]["args"][1]["args"][0]["property"], "sar:resolution_azimuth")
        self.assertEqual(a_dict["filter"]["args"][2]["args"][1]["args"][1], 45)
        a.query_dump_json()

    def test_extension_observation_sar(self):
        a = QueryBuilder()
        a.sar.observation_direction.equals(ObservationDirection.left)
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "sar:observation_direction")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], "left")
        a.query_dump_json()

    def test_extension_observation_sar_left(self):
        a = QueryBuilder()
        a.sar.observation_direction.left()
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "sar:observation_direction")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], "left")
        a.query_dump_json()

    def test_extension_observation_sar_set(self):
        a = QueryBuilder()
        a.sar.observation_direction.in_set([ObservationDirection.left])
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "in")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "sar:observation_direction")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1][0], "left")
        b = QueryBuilder()
        b.sar.observation_direction.in_set([ObservationDirection.left, ObservationDirection.right])
        b_dict = b.query_dump()
        self.assertEqual(b_dict["filter"]["args"][0]["args"][1][0], "left")
        self.assertEqual(b_dict["filter"]["args"][0]["args"][1][1], "right")
        a.query_dump_json()

    def test_number_query(self):
        a = _NumberQuery.init_with_limits("field", QueryBuilder(), None, None, is_int=True)
        self.assertRaises(ValueError, a.equals, 3.5)
        self.assertIsNotNone(a.equals(value=3.0))
        b = _NumberQuery.init_with_limits("field", QueryBuilder())
        self.assertIsNotNone(b.equals(value=3.3))

    def test_filter_or(self):
        # TODO document this user error
        a = QueryBuilder()
        raised_error = False
        try:
            a.filter((a.view.azimuth > 9) | (a.sar.observation_direction.left()))
        except AttributeError:
            raised_error = True
        self.assertTrue(raised_error)

    def test_filter_enum_serializable(self):
        a = QueryBuilder()
        a.filter((a.view.azimuth > 9) | (a.sar.observation_direction == ObservationDirection.left))
        a_dict = a.query_dump()
        json.dumps(a.query_dump())
        self.assertIsNotNone(a.query_dump_json())
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "or")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][0]["property"], "view:azimuth")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][1], 9)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][0]["property"], "sar:observation_direction")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][1], ObservationDirection.left)

    def test_boolean(self):
        a = QueryBuilder()
        a.mlm.accelerator_constrained.equals(True)
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "mlm:accelerator_constrained")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], True)
        a.query_dump_json()

    def test_dump_json(self):
        d = datetime(2024, 1, 5, 0, 1, 2, tzinfo=timezone.utc)
        a = QueryBuilder()
        a.mlm.accelerator_constrained.equals(True)
        a.datetime.lt(d)
        a.eo.cloud_cover.gt(4)
        a.geometry.intersects(Point(45, 65))
        a.proj.geometry.intersects(Point(22, 44))
        a.platform.equals("Umbra-09")
        a.mlm.framework.equals(Framework.Hugging_Face)

        dumped_json = a.query_dump_json()
        self.assertIn("2024-01-05T00:01:02+00:00", dumped_json)
        self.assertIn("\"coordinates\": [45.0", dumped_json)
        self.assertIn("\"Umbra-09\"", dumped_json)
        self.assertIn("\"Hugging Face\"", dumped_json)
        self.assertIn("\"type\": \"Point", dumped_json)
        self.assertIsNotNone(a.query_dump_json(indent=2))
        a.query_dump_json()

    def test_is_null_boolean(self):
        a = QueryBuilder()
        a.mlm.accelerator_constrained.equals(True)
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "mlm:accelerator_constrained")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], True)
        a.mlm.accelerator_constrained.is_null()
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "isNull")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "mlm:accelerator_constrained")
        self.assertEqual(1, len(a_dict["filter"]["args"][0]["args"]))
        a.query_dump_json()

    def test_is_null_enum(self):
        a = QueryBuilder()
        a.mlm.framework.is_null()
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "isNull")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "mlm:framework")
        self.assertEqual(1, len(a_dict["filter"]["args"][0]["args"]))
        a.mlm.framework.in_set([Framework.Hugging_Face, Framework.JAX])
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "in")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "mlm:framework")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], ['Hugging Face', 'JAX'])
        a.mlm.framework.is_null()
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "isNull")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "mlm:framework")
        self.assertEqual(1, len(a_dict["filter"]["args"][0]["args"]))
        a.mlm.framework.in_set([Framework.Hugging_Face, Framework.JAX])
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "in")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "mlm:framework")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], ['Hugging Face', 'JAX'])
        a.mlm.framework.not_in_set([Framework.Hugging_Face, Framework.JAX])
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "not")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["op"], "in")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][0]["property"], "mlm:framework")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][1], ['Hugging Face', 'JAX'])
        a.query_dump_json()

    def test_is_null_date_query(self):
        a = QueryBuilder()
        a.datetime.is_null()
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "isNull")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "datetime")
        self.assertEqual(1, len(a_dict["filter"]["args"][0]["args"][0]))
        a.datetime.equals(datetime.now(tz=timezone.utc))
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "datetime")
        self.assertEqual(2, len(a_dict["filter"]["args"][0]["args"]))
        a.query_dump_json()

    def test_is_null_number(self):
        a = QueryBuilder()
        a.eo.cloud_cover.gt(45)
        a.eo.cloud_cover.lt(33)
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "or")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["op"], ">")
        self.assertEqual(2, len(a_dict["filter"]["args"][0]["args"]))
        a.eo.cloud_cover.is_null()
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "isNull")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "eo:cloud_cover")
        self.assertEqual(1, len(a_dict["filter"]["args"][0]["args"][0]))
        a.query_dump_json()

    def test_is_null_spatial(self):
        a = QueryBuilder()
        a.geometry.intersects(Point(4, 5))
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "s_intersects")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "geometry")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["type"], "Point")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["coordinates"][0], 4)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["coordinates"][1], 5)
        a.geometry.is_null()
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "isNull")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "geometry")
        self.assertEqual(1, len(a_dict["filter"]["args"][0]["args"][0]))
        a.query_dump_json()

    def test_sortby_asc(self):
        a = QueryBuilder()
        a.geometry.intersects(Point(4, 5)).datetime.sort_by_asc()
        a_dict = a.query_dump()
        self.assertEqual(a_dict["sortby"][0]["field"], "datetime")
        self.assertEqual(a_dict["sortby"][0]["direction"], "asc")
        a.sar.observation_direction.sort_by_asc()
        a_dict = a.query_dump()
        self.assertEqual(a_dict["sortby"][0]["field"], "sar:observation_direction")
        self.assertEqual(a_dict["sortby"][0]["direction"], "asc")
        a.sar.observation_direction.sort_by_desc()
        a_dict = a.query_dump()
        self.assertEqual(a_dict["sortby"][0]["field"], "sar:observation_direction")
        self.assertEqual(a_dict["sortby"][0]["direction"], "desc")
        a.query_dump_json()

    def test_limit(self):
        a = QueryBuilder()
        a.geometry.intersects(Point(4, 5)).datetime.sort_by_asc()
        a_dict = a.query_dump(limit=5)
        self.assertEqual(a_dict["limit"], 5)
        a.query_dump_json()

    def test_null_projection(self):
        a = QueryBuilder()
        a.proj.bbox.is_null()
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "isNull")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "proj:bbox")
        self.assertEqual(1, len(a_dict["filter"]["args"][0]["args"][0]))
        a.query_dump_json()

    def test_uuid(self):
        input_id = uuid.uuid4()
        a = QueryBuilder()
        a.id.equals(input_id)
        a_dict = a.query_dump()
        a_json = a.query_dump_json()
        self.assertIn(str(input_id), a_json)
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "id")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], str(input_id))

    def test_uuids(self):
        input_id_1 = uuid.uuid4()
        input_id_2 = uuid.uuid4()
        a = QueryBuilder()
        a.id.in_set([input_id_1, input_id_2])
        a_dict = a.query_dump()
        a_json = a.query_dump_json()
        self.assertIn(str(input_id_1), a_json)
        self.assertIn(str(input_id_2), a_json)
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "in")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "id")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], [str(input_id_1), str(input_id_2)])

    def test_not_in_set_uuids(self):
        input_id_1 = uuid.uuid4()
        input_id_2 = uuid.uuid4()
        a = QueryBuilder()
        a.id.not_in_set([input_id_1, input_id_2])
        a_dict = a.query_dump()
        a_json = a.query_dump_json()
        self.assertIn(str(input_id_1), a_json)
        self.assertIn(str(input_id_2), a_json)
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "not")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["op"], "in")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][0]["property"], "id")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][1], [str(input_id_1), str(input_id_2)])

    def test_collection(self):
        a = QueryBuilder()
        a.collection.equals("landsat-c2-l2")
        a_dict = a.query_dump()
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "collection")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], str("landsat-c2-l2"))
        a.query_dump_json()


if __name__ == '__main__':
    unittest.main()

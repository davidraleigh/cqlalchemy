import unittest
from datetime import datetime, timedelta, timezone

from shapely import Point

from cqlalchemy.stac.query import QueryBlock


class STACTestCase(unittest.TestCase):
    def test_datetime(self):
        a = QueryBlock()
        t = datetime.now(tz=timezone.utc)
        a.datetime.lt(t)
        a_dict = a.build_query()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "<")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], t)

    def test_created(self):
        a = QueryBlock()
        t = datetime.now(tz=timezone.utc)
        a.created.lte(t)
        a_dict = a.build_query()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "<=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "created")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], t)

    def test_updated(self):
        a = QueryBlock()
        t = datetime.now(tz=timezone.utc)
        a.updated.gte(t)
        a_dict = a.build_query()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], ">=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "updated")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], t)

    def test_platform(self):
        a = QueryBlock()
        a.platform.equals("Landsat8")
        a_dict = a.build_query()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "platform")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], "Landsat8")

        a = QueryBlock()
        a.platform.like("Landsat%")
        a_dict = a.build_query()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "like")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "platform")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], "Landsat%")

    def test_gsd(self):
        a = QueryBlock()
        a.gsd.gte(0.25)
        a.gsd.lte(0.75)
        a_dict = a.build_query()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["op"], ">=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][0]["property"], "gsd")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][1], 0.25)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["op"], "<=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][0]["property"], "gsd")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][1], 0.75)

    def test_spatial(self):
        a = QueryBlock()
        a.geometry.intersects(Point(4, 5))
        a_dict = a.build_query()
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "s_intersects")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "geometry")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["type"], "Point")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["coordinates"][0], 4)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["coordinates"][1], 5)

        a.geometry.intersects(Point(4, 5).buffer(1))
        a_dict = a.build_query()
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "s_intersects")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "geometry")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["type"], "Polygon")

    def test_top_level_is_or(self):
        a = QueryBlock()
        updated = datetime.now(tz=timezone.utc)
        created = datetime.now(tz=timezone.utc)
        a.updated.gte(updated)
        a.created.lte(created)
        a_dict = a.build_query(top_level_is_or=True)

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "or")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], ">=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "updated")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], updated)
        self.assertEqual(a_dict["filter"]["args"][1]["op"], "<=")
        self.assertEqual(a_dict["filter"]["args"][1]["args"][0]["property"], "created")
        self.assertEqual(a_dict["filter"]["args"][1]["args"][1], created)

    def test_datetime_range_and(self):
        start = datetime.now(tz=timezone.utc)
        end = start + timedelta(days=1)
        a = QueryBlock()
        a.datetime.gt(start).datetime.lt(end)
        a_dict = a.build_query()
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["op"], ">")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][1], start)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["op"], "<")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][1], end)

    def test_datetime_range_or(self):
        start = datetime.now(tz=timezone.utc)
        end = start + timedelta(days=1)
        a = QueryBlock()
        a.datetime.gt(end).datetime.lt(start)
        a_dict = a.build_query()
        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "or")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["op"], "<")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1]["args"][1], start)
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["op"], ">")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["args"][1], end)

    def test_extension(self):
        a = QueryBlock()
        t = datetime.now(tz=timezone.utc)
        a.datetime.lt(t).eo.cloud_cover.lt(45).created.gt(t)
        a_dict = a.build_query()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "<")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], t)
        self.assertEqual(a_dict["filter"]["args"][1]["op"], ">")
        self.assertEqual(a_dict["filter"]["args"][1]["args"][0]["property"], "created")
        self.assertEqual(a_dict["filter"]["args"][1]["args"][1], t)
        self.assertEqual(a_dict["filter"]["args"][2]["op"], "<")
        self.assertEqual(a_dict["filter"]["args"][2]["args"][0]["property"], "eo:cloud_cover")
        self.assertEqual(a_dict["filter"]["args"][2]["args"][1], 45)


if __name__ == '__main__':
    unittest.main()

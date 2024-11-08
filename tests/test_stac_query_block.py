import unittest
from datetime import datetime, timezone

from cqlalchemy.stac.query import STACQueryBlock


class STACTestCase(unittest.TestCase):
    def test_datetime(self):
        a = STACQueryBlock()
        t = datetime.now(tz=timezone.utc)
        a.datetime.lt(t)
        a_dict = a.build_query()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "<")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "datetime")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], t)

    def test_created(self):
        a = STACQueryBlock()
        t = datetime.now(tz=timezone.utc)
        a.created.lte(t)
        a_dict = a.build_query()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "<=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "created")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], t)

    def test_updated(self):
        a = STACQueryBlock()
        t = datetime.now(tz=timezone.utc)
        a.updated.gte(t)
        a_dict = a.build_query()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], ">=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "updated")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], t)

    def test_platform(self):
        a = STACQueryBlock()
        a.platform.equals("Landsat8")
        a_dict = a.build_query()

        self.assertEqual(a_dict["filter-lang"], "cql2-json")
        self.assertEqual(a_dict["filter"]["op"], "and")
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "=")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "platform")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], "Landsat8")

        a = STACQueryBlock()
        a.platform.like("Landsat%")
        a_dict = a.build_query()
        self.assertEqual(a_dict["filter"]["args"][0]["op"], "like")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][0]["property"], "platform")
        self.assertEqual(a_dict["filter"]["args"][0]["args"][1], "Landsat%")

    def test_gsd(self):
        a = STACQueryBlock()
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


if __name__ == '__main__':
    unittest.main()

import json
import unittest
import uuid
from datetime import date, datetime, timedelta, timezone

from shapely import Point

from cqlalchemy.stac.query import (
    Framework,
    ObservationDirection,
    QueryBuilder,
    _NumberQuery,
)


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
        q2 = QueryBuilder()
        bpassed = False
        try:
            q2.filter((q2.view.azimuth > 9) | (q2.sar.observation_direction.left()))
        except AttributeError:
            bpassed = True
        assert bpassed

    def test_filter_or_2(self):
        q2 = QueryBuilder()
        bpassed = True
        try:
            q2.filter((q2.view.azimuth > 9) | (q2.sar.observation_direction == ObservationDirection.left))
        except AttributeError:
            bpassed = False
        assert bpassed

    def test_filter_enum_serializable(self):
        a = QueryBuilder()
        a.filter((a.view.azimuth > 9) | (a.sar.observation_direction == ObservationDirection.left))
        json.dumps(a.query_dump())
        self.assertIsNotNone(a.query_dump_json())

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


if __name__ == '__main__':
    unittest.main()

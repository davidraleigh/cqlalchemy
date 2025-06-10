import unittest
import uuid

from cqlalchemy.stac.query import QueryBuilder


class TestUmbraExtensionNumberFields(unittest.TestCase):
    def setUp(self):
        self.qb = QueryBuilder()

    def test_best_resolution_azimuth_meters_within_range(self):
        self.qb.umbra.best_resolution_azimuth_meters.equals(1.5)
        d = self.qb.query_dump()
        self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:best_resolution_azimuth_meters")
        self.assertEqual(d["filter"]["args"][0]["args"][1], 1.5)

    def test_best_resolution_range_meters_within_range(self):
        self.qb.umbra.best_resolution_range_meters.equals(2.0)
        d = self.qb.query_dump()
        self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:best_resolution_range_meters")
        self.assertEqual(d["filter"]["args"][0]["args"][1], 2.0)

    def test_squint_angle_degrees_off_broadside_within_range(self):
        self.qb.umbra.squint_angle_degrees_off_broadside.equals(45)
        d = self.qb.query_dump()
        self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:squint_angle_degrees_off_broadside")
        self.assertEqual(d["filter"]["args"][0]["args"][1], 45)

    def test_squint_angle_engineering_degrees_within_range(self):
        self.qb.umbra.squint_angle_engineering_degrees.equals(0)
        d = self.qb.query_dump()
        self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:squint_angle_engineering_degrees")
        self.assertEqual(d["filter"]["args"][0]["args"][1], 0)

    def test_squint_angle_exploitation_degrees_within_range(self):
        self.qb.umbra.squint_angle_exploitation_degrees.equals(-45)
        d = self.qb.query_dump()
        self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:squint_angle_exploitation_degrees")
        self.assertEqual(d["filter"]["args"][0]["args"][1], -45)

    def test_target_azimuth_angle_degrees_within_range(self):
        self.qb.umbra.target_azimuth_angle_degrees.equals(180)
        d = self.qb.query_dump()
        self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:target_azimuth_angle_degrees")
        self.assertEqual(d["filter"]["args"][0]["args"][1], 180)

    def test_best_resolution_azimuth_meters_gt(self):
        self.qb.umbra.best_resolution_azimuth_meters.gt(1.0)
        d = self.qb.query_dump()
        self.assertEqual(d["filter"]["args"][0]["op"], ">")
        self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:best_resolution_azimuth_meters")
        self.assertEqual(d["filter"]["args"][0]["args"][1], 1.0)

    def test_best_resolution_azimuth_meters_lt(self):
        self.qb.umbra.best_resolution_azimuth_meters.lt(2.0)
        d = self.qb.query_dump()
        self.assertEqual(d["filter"]["args"][0]["op"], "<")
        self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:best_resolution_azimuth_meters")
        self.assertEqual(d["filter"]["args"][0]["args"][1], 2.0)

    def test_best_resolution_azimuth_meters_gte(self):
        self.qb.umbra.best_resolution_azimuth_meters.gte(1.0)
        d = self.qb.query_dump()
        self.assertEqual(d["filter"]["args"][0]["op"], ">=")
        self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:best_resolution_azimuth_meters")
        self.assertEqual(d["filter"]["args"][0]["args"][1], 1.0)

    def test_best_resolution_azimuth_meters_lte(self):
        self.qb.umbra.best_resolution_azimuth_meters.lte(2.0)
        d = self.qb.query_dump()
        self.assertEqual(d["filter"]["args"][0]["op"], "<=")
        self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:best_resolution_azimuth_meters")
        self.assertEqual(d["filter"]["args"][0]["args"][1], 2.0)

    def test_best_resolution_azimuth_meters_not_equals(self):
        self.qb.umbra.best_resolution_azimuth_meters.not_equals(1.5)
        d = self.qb.query_dump()
        self.assertEqual(d["filter"]["args"][0]["op"], "!=")
        self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:best_resolution_azimuth_meters")
        self.assertEqual(d["filter"]["args"][0]["args"][1], 1.5)

    def test_best_resolution_azimuth_meters_is_null(self):
        self.qb.umbra.best_resolution_azimuth_meters.is_null()
        d = self.qb.query_dump()
        self.assertEqual(d["filter"]["args"][0]["op"], "isNull")
        self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:best_resolution_azimuth_meters")

    # Repeat for another field as an example
    def test_squint_angle_degrees_off_broadside_gt(self):
        self.qb.umbra.squint_angle_degrees_off_broadside.gt(10)
        d = self.qb.query_dump()
        self.assertEqual(d["filter"]["args"][0]["op"], ">")
        self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:squint_angle_degrees_off_broadside")
        self.assertEqual(d["filter"]["args"][0]["args"][1], 10)

    def test_squint_angle_degrees_off_broadside_not_equals(self):
        self.qb.umbra.squint_angle_degrees_off_broadside.not_equals(20)
        d = self.qb.query_dump()
        self.assertEqual(d["filter"]["args"][0]["op"], "!=")
        self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:squint_angle_degrees_off_broadside")
        self.assertEqual(d["filter"]["args"][0]["args"][1], 20)

    def test_squint_angle_degrees_off_broadside_is_null(self):
        self.qb.umbra.squint_angle_degrees_off_broadside.is_null()
        d = self.qb.query_dump()
        self.assertEqual(d["filter"]["args"][0]["op"], "isNull")
        self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:squint_angle_degrees_off_broadside")


class TestUmbraExtensionNumberFieldEqualsValueError(unittest.TestCase):
    def setUp(self):
        self.qb = QueryBuilder()

    def test_best_resolution_azimuth_meters_equals_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.best_resolution_azimuth_meters.equals(-0.1)

    def test_best_resolution_range_meters_equals_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.best_resolution_range_meters.equals(-0.1)

    def test_squint_angle_degrees_off_broadside_equals_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_degrees_off_broadside.equals(-0.1)

    def test_squint_angle_degrees_off_broadside_equals_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_degrees_off_broadside.equals(90.1)

    def test_squint_angle_engineering_degrees_equals_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_engineering_degrees.equals(-180.1)

    def test_squint_angle_engineering_degrees_equals_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_engineering_degrees.equals(180.1)

    def test_squint_angle_exploitation_degrees_equals_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_exploitation_degrees.equals(-90.1)

    def test_squint_angle_exploitation_degrees_equals_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_exploitation_degrees.equals(90.1)

    def test_target_azimuth_angle_degrees_equals_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.target_azimuth_angle_degrees.equals(-0.1)

    def test_target_azimuth_angle_degrees_equals_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.target_azimuth_angle_degrees.equals(360.1)


class TestUmbraExtensionNumberFieldLtLte(unittest.TestCase):
    def setUp(self):
        self.qb = QueryBuilder()

    # best_resolution_azimuth_meters: min=0, no max
    def test_best_resolution_azimuth_meters_lt_valid(self):
        self.qb.umbra.best_resolution_azimuth_meters.lt(1.0)

    def test_best_resolution_azimuth_meters_lt_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.best_resolution_azimuth_meters.lt(-0.1)

    def test_best_resolution_azimuth_meters_lte_valid(self):
        self.qb.umbra.best_resolution_azimuth_meters.lte(1.0)

    def test_best_resolution_azimuth_meters_lte_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.best_resolution_azimuth_meters.lte(-0.1)

    # best_resolution_range_meters: min=0, no max
    def test_best_resolution_range_meters_lt_valid(self):
        self.qb.umbra.best_resolution_range_meters.lt(1.0)

    def test_best_resolution_range_meters_lt_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.best_resolution_range_meters.lt(-0.1)

    def test_best_resolution_range_meters_lte_valid(self):
        self.qb.umbra.best_resolution_range_meters.lte(1.0)

    def test_best_resolution_range_meters_lte_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.best_resolution_range_meters.lte(-0.1)

    # squint_angle_degrees_off_broadside: min=0, max=90
    def test_squint_angle_degrees_off_broadside_lt_valid(self):
        self.qb.umbra.squint_angle_degrees_off_broadside.lt(45)

    def test_squint_angle_degrees_off_broadside_lt_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_degrees_off_broadside.lt(-0.1)

    def test_squint_angle_degrees_off_broadside_lt_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_degrees_off_broadside.lt(90.1)

    def test_squint_angle_degrees_off_broadside_lte_valid(self):
        self.qb.umbra.squint_angle_degrees_off_broadside.lte(45)

    def test_squint_angle_degrees_off_broadside_lte_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_degrees_off_broadside.lte(-0.1)

    def test_squint_angle_degrees_off_broadside_lte_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_degrees_off_broadside.lte(90.1)

    # squint_angle_engineering_degrees: min=-180, max=180
    def test_squint_angle_engineering_degrees_lt_valid(self):
        self.qb.umbra.squint_angle_engineering_degrees.lt(0)

    def test_squint_angle_engineering_degrees_lt_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_engineering_degrees.lt(-180.1)

    def test_squint_angle_engineering_degrees_lt_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_engineering_degrees.lt(180.1)

    def test_squint_angle_engineering_degrees_lte_valid(self):
        self.qb.umbra.squint_angle_engineering_degrees.lte(0)

    def test_squint_angle_engineering_degrees_lte_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_engineering_degrees.lte(-180.1)

    def test_squint_angle_engineering_degrees_lte_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_engineering_degrees.lte(180.1)

    # squint_angle_exploitation_degrees: min=-90, max=90
    def test_squint_angle_exploitation_degrees_lt_valid(self):
        self.qb.umbra.squint_angle_exploitation_degrees.lt(0)

    def test_squint_angle_exploitation_degrees_lt_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_exploitation_degrees.lt(-90.1)

    def test_squint_angle_exploitation_degrees_lt_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_exploitation_degrees.lt(90.1)

    def test_squint_angle_exploitation_degrees_lte_valid(self):
        self.qb.umbra.squint_angle_exploitation_degrees.lte(0)

    def test_squint_angle_exploitation_degrees_lte_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_exploitation_degrees.lte(-90.1)

    def test_squint_angle_exploitation_degrees_lte_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_exploitation_degrees.lte(90.1)

    # target_azimuth_angle_degrees: min=0, max=360
    def test_target_azimuth_angle_degrees_lt_valid(self):
        self.qb.umbra.target_azimuth_angle_degrees.lt(180)

    def test_target_azimuth_angle_degrees_lt_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.target_azimuth_angle_degrees.lt(-0.1)

    def test_target_azimuth_angle_degrees_lt_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.target_azimuth_angle_degrees.lt(360.1)

    def test_target_azimuth_angle_degrees_lte_valid(self):
        self.qb.umbra.target_azimuth_angle_degrees.lte(180)

    def test_target_azimuth_angle_degrees_lte_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.target_azimuth_angle_degrees.lte(-0.1)

    def test_target_azimuth_angle_degrees_lte_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.target_azimuth_angle_degrees.lte(360.1)


class TestUmbraExtensionNumberFieldGtGte(unittest.TestCase):
    def setUp(self):
        self.qb = QueryBuilder()

    # best_resolution_azimuth_meters: min=0, no max
    def test_best_resolution_azimuth_meters_gt_valid(self):
        self.qb.umbra.best_resolution_azimuth_meters.gt(1.0)

    def test_best_resolution_azimuth_meters_gt_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.best_resolution_azimuth_meters.gt(-0.1)

    def test_best_resolution_azimuth_meters_gte_valid(self):
        self.qb.umbra.best_resolution_azimuth_meters.gte(1.0)

    def test_best_resolution_azimuth_meters_gte_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.best_resolution_azimuth_meters.gte(-0.1)

    # best_resolution_range_meters: min=0, no max
    def test_best_resolution_range_meters_gt_valid(self):
        self.qb.umbra.best_resolution_range_meters.gt(1.0)

    def test_best_resolution_range_meters_gt_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.best_resolution_range_meters.gt(-0.1)

    def test_best_resolution_range_meters_gte_valid(self):
        self.qb.umbra.best_resolution_range_meters.gte(1.0)

    def test_best_resolution_range_meters_gte_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.best_resolution_range_meters.gte(-0.1)

    # squint_angle_degrees_off_broadside: min=0, max=90
    def test_squint_angle_degrees_off_broadside_gt_valid(self):
        self.qb.umbra.squint_angle_degrees_off_broadside.gt(45)

    def test_squint_angle_degrees_off_broadside_gt_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_degrees_off_broadside.gt(-0.1)

    def test_squint_angle_degrees_off_broadside_gt_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_degrees_off_broadside.gt(90.1)

    def test_squint_angle_degrees_off_broadside_gte_valid(self):
        self.qb.umbra.squint_angle_degrees_off_broadside.gte(45)

    def test_squint_angle_degrees_off_broadside_gte_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_degrees_off_broadside.gte(-0.1)

    def test_squint_angle_degrees_off_broadside_gte_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_degrees_off_broadside.gte(90.1)

    # squint_angle_engineering_degrees: min=-180, max=180
    def test_squint_angle_engineering_degrees_gt_valid(self):
        self.qb.umbra.squint_angle_engineering_degrees.gt(0)

    def test_squint_angle_engineering_degrees_gt_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_engineering_degrees.gt(-180.1)

    def test_squint_angle_engineering_degrees_gt_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_engineering_degrees.gt(180.1)

    def test_squint_angle_engineering_degrees_gte_valid(self):
        self.qb.umbra.squint_angle_engineering_degrees.gte(0)

    def test_squint_angle_engineering_degrees_gte_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_engineering_degrees.gte(-180.1)

    def test_squint_angle_engineering_degrees_gte_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_engineering_degrees.gte(180.1)

    # squint_angle_exploitation_degrees: min=-90, max=90
    def test_squint_angle_exploitation_degrees_gt_valid(self):
        self.qb.umbra.squint_angle_exploitation_degrees.gt(0)

    def test_squint_angle_exploitation_degrees_gt_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_exploitation_degrees.gt(-90.1)

    def test_squint_angle_exploitation_degrees_gt_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_exploitation_degrees.gt(90.1)

    def test_squint_angle_exploitation_degrees_gte_valid(self):
        self.qb.umbra.squint_angle_exploitation_degrees.gte(0)

    def test_squint_angle_exploitation_degrees_gte_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_exploitation_degrees.gte(-90.1)

    def test_squint_angle_exploitation_degrees_gte_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.squint_angle_exploitation_degrees.gte(90.1)

    # target_azimuth_angle_degrees: min=0, max=360
    def test_target_azimuth_angle_degrees_gt_valid(self):
        self.qb.umbra.target_azimuth_angle_degrees.gt(180)

    def test_target_azimuth_angle_degrees_gt_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.target_azimuth_angle_degrees.gt(-0.1)

    def test_target_azimuth_angle_degrees_gt_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.target_azimuth_angle_degrees.gt(360.1)

    def test_target_azimuth_angle_degrees_gte_valid(self):
        self.qb.umbra.target_azimuth_angle_degrees.gte(180)

    def test_target_azimuth_angle_degrees_gte_below_min(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.target_azimuth_angle_degrees.gte(-0.1)

    def test_target_azimuth_angle_degrees_gte_above_max(self):
        with self.assertRaises(ValueError):
            self.qb.umbra.target_azimuth_angle_degrees.gte(360.1)


class TestUmbraExtensionStringFields(unittest.TestCase):
    def setUp(self):
        self.qb = QueryBuilder()

    def test_collect_id_equals_with_string_and_uuid(self):
        for val in ["abc123", uuid.uuid4()]:
            with self.subTest(val=val):
                self.qb.umbra.collect_id.equals(val)
                d = self.qb.query_dump()
                self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:collect_id")
                self.assertEqual(str(d["filter"]["args"][0]["args"][1]), str(val))

    def test_collect_id_not_equals_with_string_and_uuid(self):
        for val in ["abc123", uuid.uuid4()]:
            with self.subTest(val=val):
                self.qb.umbra.collect_id.not_equals(val)
                d = self.qb.query_dump()
                self.assertEqual(d["filter"]["args"][0]["op"], "!=")
                self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:collect_id")
                self.assertEqual(str(d["filter"]["args"][0]["args"][1]), str(val))

    def test_collect_id_in_set_with_string_and_uuid(self):
        vals = ["abc123", str(uuid.uuid4())]
        self.qb.umbra.collect_id.in_set(vals)
        d = self.qb.query_dump()
        self.assertEqual(d["filter"]["args"][0]["op"], "in")
        self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:collect_id")
        self.assertEqual([str(v) for v in d["filter"]["args"][0]["args"][1]], vals)

    def test_collect_id_not_in_set_with_string_and_uuid(self):
        vals = ["abc123", str(uuid.uuid4())]
        self.qb.umbra.collect_id.not_in_set(vals)
        d = self.qb.query_dump()
        self.assertEqual(d["filter"]["args"][0]["op"], "not")
        inner = d["filter"]["args"][0]["args"][0]
        self.assertEqual(inner["op"], "in")
        self.assertEqual(inner["args"][0]["property"], "umbra:collect_id")
        self.assertEqual([str(v) for v in inner["args"][1]], vals)

    def test_task_id_equals_with_string_and_uuid(self):
        for val in ["task-xyz", uuid.uuid4()]:
            with self.subTest(val=val):
                self.qb.umbra.task_id.equals(val)
                d = self.qb.query_dump()
                self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:task_id")
                self.assertEqual(str(d["filter"]["args"][0]["args"][1]), str(val))

    def test_task_id_not_equals_with_string_and_uuid(self):
        for val in ["task-xyz", uuid.uuid4()]:
            with self.subTest(val=val):
                self.qb.umbra.task_id.not_equals(val)
                d = self.qb.query_dump()
                self.assertEqual(d["filter"]["args"][0]["op"], "!=")
                self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:task_id")
                self.assertEqual(str(d["filter"]["args"][0]["args"][1]), str(val))

    def test_task_id_in_set_with_string_and_uuid(self):
        vals = ["task-xyz", str(uuid.uuid4())]
        self.qb.umbra.task_id.in_set(vals)
        d = self.qb.query_dump()
        self.assertEqual(d["filter"]["args"][0]["op"], "in")
        self.assertEqual(d["filter"]["args"][0]["args"][0]["property"], "umbra:task_id")
        self.assertEqual([str(v) for v in d["filter"]["args"][0]["args"][1]], vals)

    def test_task_id_not_in_set_with_string_and_uuid(self):
        vals = ["task-xyz", str(uuid.uuid4())]
        self.qb.umbra.task_id.not_in_set(vals)
        d = self.qb.query_dump()
        self.assertEqual(d["filter"]["args"][0]["op"], "not")
        inner = d["filter"]["args"][0]["args"][0]
        self.assertEqual(inner["op"], "in")
        self.assertEqual(inner["args"][0]["property"], "umbra:task_id")
        self.assertEqual([str(v) for v in inner["args"][1]], vals)

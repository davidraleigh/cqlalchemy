import json
import pkgutil
from unittest import TestCase

from cqlalchemy.scaffold.build import ExtensionBuilder, build_enum, build_query_file

eo_definition = json.loads(pkgutil.get_data(__name__, "test_data/eo.schema.json").decode('utf-8'))
sar_definition = json.loads(pkgutil.get_data(__name__, "test_data/sar.schema.json").decode('utf-8'))
view_definition = json.loads(pkgutil.get_data(__name__, "test_data/view.schema.json").decode('utf-8'))
sat_definition = json.loads(pkgutil.get_data(__name__, "test_data/sat.schema.json").decode('utf-8'))
view_1_expected = pkgutil.get_data(__name__, "test_data/view.py.txt").decode('utf-8')
sat_1_expected = pkgutil.get_data(__name__, "test_data/sat.py.txt").decode('utf-8')
sar_1_expected = pkgutil.get_data(__name__, "test_data/sar.py.txt").decode('utf-8')
eo_1_expected = pkgutil.get_data(__name__, "test_data/eo.py.txt").decode('utf-8')

query_1_expected = pkgutil.get_data(__name__, "test_data/query_1.py").decode('utf-8')
query_2_expected = pkgutil.get_data(__name__, "test_data/query_2.py").decode('utf-8')


class TestBuild(TestCase):
    def test_enum_build_1(self):
        input_key = "sar:observation_direction"
        input_obj = {
          "title": "Antenna pointing direction",
          "type": "string",
          "enum": [
            "left",
            "right"
          ]
        }
        expected = """class ObservationDirection(Enum):
    left = "left"
    right = "right"


class ObservationDirectionQuery(EnumQuery):
    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBlock, enum_fields: list[str]):
        o = ObservationDirectionQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: ObservationDirection) -> QueryBlock:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def in_set(self, values: list[ObservationDirection]) -> QueryBlock:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj

    def left(self) -> QueryBlock:
        return self.equals(ObservationDirection.left)

    def right(self) -> QueryBlock:
        return self.equals(ObservationDirection.right)
"""
        expected_lines = expected.split("\n")
        actual, _ = build_enum(input_key, input_obj, add_unique=True)
        actual_lines = actual.split("\n")
        for a in zip(expected_lines, actual_lines):
            if a[0] != a[1]:
                self.assertEqual(a[0], a[1])
        self.assertEqual(expected, actual)

    def test_enum_build_2(self):
        input_key = "sar:frequency_band"
        input_obj = {
          "title": "Frequency Band",
          "type": "string",
          "enum": [
            "P",
            "L",
            "S",
            "C",
            "X",
            "Ku",
            "K",
            "Ka"
          ]
        }
        expected = """class FrequencyBand(Enum):
    P = "P"
    L = "L"
    S = "S"
    C = "C"
    X = "X"
    Ku = "Ku"
    K = "K"
    Ka = "Ka"


class FrequencyBandQuery(EnumQuery):
    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBlock, enum_fields: list[str]):
        o = FrequencyBandQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: FrequencyBand) -> QueryBlock:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def in_set(self, values: list[FrequencyBand]) -> QueryBlock:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj
"""
        expected_lines = expected.split("\n")
        actual, _ = build_enum(input_key, input_obj)
        actual_lines = actual.split("\n")
        for a in zip(expected_lines, actual_lines):
            if a[0] != a[1]:
                self.assertEqual(a[0], a[1])
        self.assertEqual(expected, actual)

    def test_enum_build_3(self):
        input_key = "sar:observation_direction"
        input_obj = {
          "title": "Antenna pointing direction",
          "type": "string",
          "enum": [
            "left",
            "right"
          ]
        }
        expected = """class SARObservationDirection(Enum):
    left = "left"
    right = "right"


class SARObservationDirectionQuery(EnumQuery):
    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBlock, enum_fields: list[str]):
        o = SARObservationDirectionQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: SARObservationDirection) -> QueryBlock:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def in_set(self, values: list[SARObservationDirection]) -> QueryBlock:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj

    def left(self) -> QueryBlock:
        return self.equals(SARObservationDirection.left)

    def right(self) -> QueryBlock:
        return self.equals(SARObservationDirection.right)
"""
        expected_lines = expected.split("\n")
        actual, _ = build_enum(input_key, input_obj, full_name=True, add_unique=True)
        actual_lines = actual.split("\n")
        for a in zip(expected_lines, actual_lines):
            if a[0] != a[1]:
                self.assertEqual(a[0], a[1])
        self.assertEqual(expected, actual)

    def test_extension_eo_1(self):
        expected_lines = eo_1_expected.split("\n")
        actual = ExtensionBuilder(eo_definition).extension
        actual_lines = actual.split("\n")
        for a in zip(expected_lines, actual_lines):
            if a[0] != a[1]:
                self.assertEqual(a[0], a[1])
        self.assertEqual(eo_1_expected, actual)

    def test_extension_sar_1(self):
        expected_lines = sar_1_expected.split("\n")
        actual = ExtensionBuilder(sar_definition).extension
        actual_lines = actual.split("\n")
        for a in zip(expected_lines, actual_lines):
            if a[0] != a[1]:
                self.assertEqual(a[0], a[1])
        self.assertEqual(sar_1_expected, actual)

    def test_extension_view_1(self):
        expected_lines = view_1_expected.split("\n")
        actual = ExtensionBuilder(view_definition).extension
        actual_lines = actual.split("\n")
        for a in zip(expected_lines, actual_lines):
            if a[0] != a[1]:
                self.assertEqual(a[0], a[1])
        self.assertEqual(view_1_expected, actual)

    def test_extension_sat_1(self):
        expected_lines = sat_1_expected.split("\n")
        actual = ExtensionBuilder(sat_definition).extension
        actual_lines = actual.split("\n")
        for a in zip(expected_lines, actual_lines):
            if a[0] != a[1]:
                self.assertEqual(a[0], a[1])
        self.assertEqual(sat_1_expected, actual)

    def test_query_py_1(self):
        expected_lines = query_1_expected.split("\n")
        actual = build_query_file([eo_definition, sar_definition, view_definition, sat_definition])
        actual_lines = actual.split("\n")
        for a in zip(expected_lines, actual_lines):
            if a[0] != a[1]:
                self.assertEqual(a[0], a[1])
        self.assertEqual(query_1_expected, actual)

    def test_query_py_2(self):
        expected_lines = query_2_expected.split("\n")
        fields_to_exclude = ["gsd",
                             "mission",
                             "constellation",
                             "sat:absolute_orbit",
                             "sat:anx_datetime",
                             "sat:platform_international_designator",
                             "sat:relative_orbit",
                             "view:off_nadir",
                             "view:sun_azimuth",
                             "view:sun_elevation",
                             "sar:looks_equivalent_number",
                             "sar:pixel_spacing_azimuth",
                             "sar:pixel_spacing_range",
                             ]
        actual = build_query_file(
            [sar_definition, view_definition, sat_definition],
            fields_to_exclude=fields_to_exclude)
        actual_lines = actual.split("\n")
        for a in zip(expected_lines, actual_lines):
            if a[0] != a[1]:
                self.assertEqual(a[0], a[1])
        self.assertEqual(query_2_expected, actual)

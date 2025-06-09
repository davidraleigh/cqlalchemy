import json
import pkgutil
from unittest import TestCase

import pytest
import requests

from cqlalchemy.scaffold.build import ExtensionBuilder, build_enum, build_query_file

eo_definition = json.loads(pkgutil.get_data(__name__, "test_data/eo.schema.json").decode('utf-8'))
sar_definition = json.loads(pkgutil.get_data(__name__, "test_data/sar.schema.json").decode('utf-8'))
view_definition = json.loads(pkgutil.get_data(__name__, "test_data/view.schema.json").decode('utf-8'))
sat_definition = json.loads(pkgutil.get_data(__name__, "test_data/sat.schema.json").decode('utf-8'))
mlm_definition = json.loads(pkgutil.get_data(__name__, "test_data/mlm.schema.json").decode('utf-8'))
landsat_definition = json.loads(pkgutil.get_data(__name__, "test_data/landsat.schema.json").decode('utf-8'))
planet_definition = json.loads(pkgutil.get_data(__name__, "test_data/planet.schema.json").decode('utf-8'))

eo_1_expected = pkgutil.get_data(__name__, "test_data/eo.py.txt").decode('utf-8')
sar_1_expected = pkgutil.get_data(__name__, "test_data/sar.py.txt").decode('utf-8')
view_1_expected = pkgutil.get_data(__name__, "test_data/view.py.txt").decode('utf-8')
sat_1_expected = pkgutil.get_data(__name__, "test_data/sat.py.txt").decode('utf-8')
mlm_1_expected = pkgutil.get_data(__name__, "test_data/mlm.py.txt").decode('utf-8')
landsat_1_expected = pkgutil.get_data(__name__, "test_data/landsat.py.txt").decode('utf-8')
planet_1_expected = pkgutil.get_data(__name__, "test_data/planet.py.txt").decode('utf-8')

query_1_expected = pkgutil.get_data(__name__, "test_data/query_1.py").decode('utf-8')
query_2_expected = pkgutil.get_data(__name__, "test_data/query_2.py").decode('utf-8')
extension_list = pkgutil.get_data(__name__, "test_data/extension_list.txt").decode('utf-8')


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
        expected = """class SARObservationDirectionEnum(str, Enum):
    \"\"\"
    SAR Observation Direction Enum
    \"\"\"

    left = "left"
    right = "right"


class _SARObservationDirectionEnumQuery(_EnumQuery):
    \"\"\"
    SAR Observation Direction Enum Query Interface
    \"\"\"

    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBuilder, enum_fields: list[str]):
        o = _SARObservationDirectionEnumQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: SARObservationDirectionEnum) -> QueryBuilder:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def not_equals(self, value: SARObservationDirectionEnum) -> QueryBuilder:
        self._check([value.value])
        self._ne_value = value.value
        return self._parent_obj

    def in_set(self, values: list[SARObservationDirectionEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj

    def not_in_set(self, values: list[SARObservationDirectionEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._not_in_values = extracted
        return self._parent_obj

    def left(self) -> QueryBuilder:
        return self.equals(SARObservationDirectionEnum.left)

    def right(self) -> QueryBuilder:
        return self.equals(SARObservationDirectionEnum.right)
"""
        expected_lines = expected.split("\n")
        actual, _ = build_enum(input_key, input_obj, full_enum_name=True, add_unique=True)
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
        expected = """class SARFrequencyBandEnum(str, Enum):
    \"\"\"
    SAR Frequency Band Enum
    \"\"\"

    P = "P"
    L = "L"
    S = "S"
    C = "C"
    X = "X"
    Ku = "Ku"
    K = "K"
    Ka = "Ka"


class _SARFrequencyBandEnumQuery(_EnumQuery):
    \"\"\"
    SAR Frequency Band Enum Query Interface
    \"\"\"

    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBuilder, enum_fields: list[str]):
        o = _SARFrequencyBandEnumQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: SARFrequencyBandEnum) -> QueryBuilder:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def not_equals(self, value: SARFrequencyBandEnum) -> QueryBuilder:
        self._check([value.value])
        self._ne_value = value.value
        return self._parent_obj

    def in_set(self, values: list[SARFrequencyBandEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj

    def not_in_set(self, values: list[SARFrequencyBandEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._not_in_values = extracted
        return self._parent_obj
"""
        expected_lines = expected.split("\n")
        actual, _ = build_enum(input_key, input_obj, full_enum_name=True)
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
        expected = """class SARObservationDirectionEnum(str, Enum):
    \"\"\"
    SAR Observation Direction Enum
    \"\"\"

    left = "left"
    right = "right"


class _SARObservationDirectionEnumQuery(_EnumQuery):
    \"\"\"
    SAR Observation Direction Enum Query Interface
    \"\"\"

    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBuilder, enum_fields: list[str]):
        o = _SARObservationDirectionEnumQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: SARObservationDirectionEnum) -> QueryBuilder:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def not_equals(self, value: SARObservationDirectionEnum) -> QueryBuilder:
        self._check([value.value])
        self._ne_value = value.value
        return self._parent_obj

    def in_set(self, values: list[SARObservationDirectionEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj

    def not_in_set(self, values: list[SARObservationDirectionEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._not_in_values = extracted
        return self._parent_obj

    def left(self) -> QueryBuilder:
        return self.equals(SARObservationDirectionEnum.left)

    def right(self) -> QueryBuilder:
        return self.equals(SARObservationDirectionEnum.right)
"""
        expected_lines = expected.split("\n")
        actual, _ = build_enum(input_key, input_obj, full_enum_name=True, add_unique=True)
        actual_lines = actual.split("\n")
        for a in zip(expected_lines, actual_lines):
            if a[0] != a[1]:
                self.assertEqual(a[0], a[1])
        self.assertEqual(expected, actual)

    def test_extension_eo_1(self):
        expected_lines = eo_1_expected.split("\n")
        actual = ExtensionBuilder(eo_definition, full_enum_name=True).extension
        actual_lines = actual.split("\n")
        for a in zip(expected_lines, actual_lines):
            if a[0] != a[1]:
                self.assertEqual(a[0], a[1])
        self.assertEqual(eo_1_expected, actual)

    def test_extension_sar_1(self):
        expected_lines = sar_1_expected.split("\n")
        actual = ExtensionBuilder(sar_definition, full_enum_name=True).extension
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
        actual = ExtensionBuilder(sat_definition, full_enum_name=True).extension
        actual_lines = actual.split("\n")
        for a in zip(expected_lines, actual_lines):
            if a[0] != a[1]:
                self.assertEqual(a[0], a[1])
        self.assertEqual(sat_1_expected, actual)

    def test_extension_landsat_1(self):
        expected_lines = landsat_1_expected.split("\n")
        actual = ExtensionBuilder(landsat_definition, full_enum_name=True).extension
        actual_lines = actual.split("\n")
        for a in zip(expected_lines, actual_lines):
            if a[0] != a[1]:
                self.assertEqual(a[0], a[1])
        self.assertEqual(landsat_1_expected, actual)

    def test_extension_mlm_1(self):
        expected_lines = mlm_1_expected.split("\n")
        actual = ExtensionBuilder(mlm_definition, full_enum_name=True).extension
        actual_lines = actual.split("\n")
        for a in zip(expected_lines, actual_lines):
            if a[0] != a[1]:
                self.assertEqual(a[0], a[1])
        self.assertEqual(mlm_1_expected, actual)

    def test_query_py_1(self):
        expected_lines = query_1_expected.split("\n")
        actual = build_query_file([eo_definition, sar_definition, sat_definition, view_definition],
                                  full_enum_name=True)
        actual_lines = actual.split("\n")
        for a in zip(expected_lines, actual_lines):
            if a[0] != a[1]:
                if a[0].startswith("# generated on 20"):
                    continue
                self.assertEqual(a[0], a[1])

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
            [sar_definition, sat_definition, view_definition],
            fields_to_exclude=fields_to_exclude,
            add_unique_enum=True,
            full_enum_name=True)
        actual_lines = actual.split("\n")
        for a in zip(expected_lines, actual_lines):
            if a[0] != a[1]:
                if a[0].startswith("# generated on 20"):
                    continue
                self.assertEqual(a[0], a[1])

    def test_planet_1(self):
        expected_lines = planet_1_expected.split("\n")
        actual = ExtensionBuilder(planet_definition, full_enum_name=True).extension
        actual_lines = actual.split("\n")
        for a in zip(expected_lines, actual_lines):
            if a[0] != a[1]:
                self.assertEqual(a[0], a[1])
        self.assertEqual(planet_1_expected, actual)


@pytest.mark.integration
class TestExtensionList(TestCase):
    def test_stac_extensions(self):
        for ext_url in extension_list.split("\n"):
            schema_request = requests.get(ext_url)
            if schema_request.status_code != 200:
                print(f"skipped {ext_url}")
            try:
                ExtensionBuilder(schema_request.json())
            except BaseException as be:
                assert False, f"{ext_url} and {be}"

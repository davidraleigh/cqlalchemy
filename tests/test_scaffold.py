import json
import pkgutil
from unittest import TestCase

from cqlalchemy.scaffold.build import build_enum, build_extension

eo_definition = json.loads(pkgutil.get_data(__name__, "test_data/eo.schema.json").decode('utf-8'))


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
        actual = build_enum(input_key, input_obj, add_unique=True)
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
        actual = build_enum(input_key, input_obj)
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
        actual = build_enum(input_key, input_obj, full_name=True, add_unique=True)
        actual_lines = actual.split("\n")
        for a in zip(expected_lines, actual_lines):
            if a[0] != a[1]:
                self.assertEqual(a[0], a[1])
        self.assertEqual(expected, actual)

    def test_extension_eo_1(self):
        expected = """class EOExtension(Extension):
    \"\"\"
    STAC EO Extension for STAC Items and STAC Collections.
    \"\"\"
    def __init__(self, query_block: QueryBlock):
        super().__init__(query_block)
        self.center_wavelength = NumberQuery.init_with_limits("eo:center_wavelength", query_block, min_value=None, max_value=None)
        self.cloud_cover = NumberQuery.init_with_limits("eo:cloud_cover", query_block, min_value=0, max_value=100)
        self.common_name = StringQuery("eo:common_name", self)
        self.full_width_half_max = NumberQuery.init_with_limits("eo:full_width_half_max", query_block, min_value=None, max_value=None)
        self.snow_cover = NumberQuery.init_with_limits("eo:snow_cover", query_block, min_value=0, max_value=100)
        self.solar_illumination = NumberQuery.init_with_limits("eo:solar_illumination", query_block, min_value=0, max_value=None)
"""
        expected_lines = expected.split("\n")
        actual = build_extension(eo_definition)
        actual_lines = actual.split("\n")
        for a in zip(expected_lines, actual_lines):
            if a[0] != a[1]:
                self.assertEqual(a[0], a[1])
        self.assertEqual(expected, actual)

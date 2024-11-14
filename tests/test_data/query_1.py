# This file is generated with version 0.0.1 of cqlalchemy https://github.com/davidraleigh/cqlalchemy

from __future__ import annotations

import math
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from json import JSONEncoder

from shapely.geometry.base import BaseGeometry


class DateTimeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()


class QueryTuple:
    def __init__(self, left, op: str, right):
        self.left = left
        self.op = op
        self.right = right

    def __or__(self, other):
        value = QueryTuple(self, "|", other)
        if value.check_parents(bad_op="&"):
            raise ValueError("can't mix '&' and '|' in `filter` function. must be all 'or', "
                             "or all 'and' (except inside of the 'filter_grouping' function)")
        return value

    def __and__(self, other):
        value = QueryTuple(self, "&", other)
        if value.check_parents(bad_op="|"):
            raise ValueError("can't mix '&' and '|' in `filter` function. must be all 'or', "
                             "or all 'and' (except inside of the 'filter_grouping' function)")
        return value

    def check_parents(self, bad_op):
        if isinstance(self.left, QueryBase):
            return False

        if isinstance(self.left, FilterTuple):
            if self.right.check_parents(bad_op):
                return True
            return False
        if isinstance(self.right, FilterTuple):
            if self.left.check_parents(bad_op):
                return True
            return False

        if self.op == bad_op:
            return True
        if self.left.check_parents(bad_op):
            return True
        if self.right.check_parents(bad_op):
            return True
        return False

    @staticmethod
    def _build_query(query_tuple: QueryTuple, filter_query: dict):
        if isinstance(query_tuple.left, QueryBase):
            filter_query["args"].append({"op": query_tuple.op,
                                         "args": [query_tuple.left.property_obj, query_tuple.right]})
        elif isinstance(query_tuple.left, FilterTuple):
            filter_query["args"].append(query_tuple.left.build_query())
            QueryTuple._build_query(query_tuple.right, filter_query)
        elif isinstance(query_tuple.right, FilterTuple):
            filter_query["args"].append(query_tuple.right.build_query())
            QueryTuple._build_query(query_tuple.left, filter_query)
        else:
            QueryTuple._build_query(query_tuple.left, filter_query)
            QueryTuple._build_query(query_tuple.right, filter_query)
        return filter_query

    def build_query(self):
        filter_query = {"op": "and", "args": []}
        filter_query = QueryTuple._build_query(self, filter_query)
        if self.op == "|":
            filter_query["op"] = "or"
        return filter_query


class FilterTuple(QueryTuple):
    pass


class QueryBase:
    def __init__(self, field_name, parent_obj: QueryBlock):
        self._field_name = field_name
        self._parent_obj = parent_obj

    def build_query(self):
        pass

    def __eq__(self, other):
        return QueryTuple(self, "=", other)

    def __gt__(self, other):
        self._greater_check(other)
        return QueryTuple(self, ">", other)

    def __ge__(self, other):
        self._greater_check(other)
        return QueryTuple(self, ">=", other)

    def __lt__(self, other):
        self._less_check(other)
        return QueryTuple(self, "<", other)

    def __le__(self, other):
        self._less_check(other)
        return QueryTuple(self, "<=", other)

    @property
    def property_obj(self):
        return {"property": self._field_name}

    def _greater_check(self, value):
        pass

    def _less_check(self, value):
        pass

    def _check(self, value):
        pass


class BooleanQuery(QueryBase):
    _eq_value = None

    def equals(self, value: str) -> QueryBlock:
        self._eq_value = value
        return self._parent_obj

    def build_query(self):
        if self._eq_value is not None:
            return {
                "op": "=",
                "args": [self.property_obj, self._eq_value]
            }
        return None


class BaseString(QueryBase):
    _eq_value = None
    _in_values = None
    _like_value = None

    def build_query(self):
        if self._eq_value is not None:
            return {
                "op": "=",
                "args": [self.property_obj, self._eq_value]
            }
        elif self._in_values is not None and len(self._in_values) > 0:
            return {
                "op": "in",
                "args": [
                    self.property_obj,
                    self._in_values
                ]
            }
        elif self._like_value is not None:
            return {
                "op": "like",
                "args": [
                    self.property_obj,
                    self._like_value
                ]
            }
        return None


class EnumQuery(BaseString):
    _enum_values: set[str] = set()

    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBlock, enum_fields: list[str]):
        c = EnumQuery(field_name, parent_obj)
        c._enum_values = set(enum_fields)
        if len(c._enum_values) <= 1:
            raise ValueError(f"enum_fields must have 2 or more unique values. fields are {enum_fields}")
        return c

    def _check(self, values: list[str]):
        if not set(values).issubset(self._enum_values):
            raise ValueError("")
        if self._in_values is not None or self._eq_value is not None or self._like_value is not None:
            raise ValueError("eq, in or like cannot already be set")


class StringQuery(BaseString):
    def equals(self, value: str) -> QueryBlock:
        self._check(value)
        self._eq_value = value
        return self._parent_obj

    def in_set(self, values: list[str]) -> QueryBlock:
        self._check(values)
        self._in_values = values
        return self._parent_obj

    def like(self, value: str) -> QueryBlock:
        self._check(value)
        self._like_value = value
        return self._parent_obj

    def _check(self, value):
        if self._in_values is not None or self._eq_value is not None or self._like_value is not None:
            raise ValueError("eq, in or like cannot already be set")


class Query(QueryBase):
    _gt_value = None
    _gt_operand = None
    _lt_value = None
    _lt_operand = None
    _eq_value = None

    def build_query(self):
        if self._eq_value is not None:
            return {
                "op": "=",
                "args": [self.property_obj, self._eq_value]
            }
        elif self._gt_value is None and self._lt_value is None:
            return None

        gt_query = {
            "op": self._gt_operand,
            "args": [self.property_obj, self._gt_value]
        }
        lt_query = {
            "op": self._lt_operand,
            "args": [self.property_obj, self._lt_value]
        }
        if self._gt_value is not None and self._lt_value is None:
            return gt_query
        elif self._lt_value is not None and self._gt_value is None:
            return lt_query
        elif self._gt_value is not None and self._lt_value is not None and self._gt_value < self._lt_value:
            return {
                "op": "and",
                "args": [
                    gt_query, lt_query
                ]
            }
        elif self._gt_value is not None and self._lt_value is not None and self._gt_value > self._lt_value:
            return {
                "op": "or",
                "args": [
                    gt_query, lt_query
                ]
            }

    def equals(self, value) -> QueryBlock:
        self._check(value)
        self._eq_value = value
        return self._parent_obj

    def gt(self, value) -> QueryBlock:
        self._check(value)
        self._greater_check(value)
        self._gt_value = value
        self._gt_operand = ">"
        return self._parent_obj

    def gte(self, value) -> QueryBlock:
        self._check(value)
        self._greater_check(value)
        self._gt_value = value
        self._gt_operand = ">="
        return self._parent_obj

    def lt(self, value) -> QueryBlock:
        self._check(value)
        self._less_check(value)
        self._lt_value = value
        self._lt_operand = "<"
        return self._parent_obj

    def lte(self, value) -> QueryBlock:
        self._check(value)
        self._less_check(value)
        self._lt_value = value
        self._lt_operand = "<="
        return self._parent_obj

    # def _greater_check(self, value):
    #     if self._gt_operand is not None or self._eq_value is not None:
    #         raise ValueError("cannot set equals after setting gt,gte,equals")
    #
    # def _less_check(self, value):
    #     if self._lt_operand is not None or self._eq_value is not None:
    #         raise ValueError("cannot set less after setting lt,lte,equals")
    #
    # def _equals_check(self):
    #     if self._gt_value is not None or self._lt_value is not None or self._eq_value is not None:
    #         raise ValueError("cannot set equals after setting lt,lte,gt,gte,equals")


class DateQuery(Query):
    def equals(self, value: date, tzinfo=timezone.utc) -> QueryBlock:
        # self._equals_check()
        if isinstance(value, date):
            start = datetime.combine(value, datetime.min.time(), tzinfo=tzinfo)
            end = datetime.combine(value, datetime.max.time(), tzinfo=tzinfo)
            self._gt_value = start
            self._gt_operand = ">="
            self._lt_value = end
            self._lt_operand = "<="
        else:
            self._eq_value = date
        return self._parent_obj

    def delta(self, value: date, td: timedelta, tzinfo=timezone.utc):
        # self._equals_check()
        if td.total_seconds() > 0:
            start = datetime.combine(value, datetime.min.time(), tzinfo=tzinfo)
            end = start + td
        else:
            end = datetime.combine(value, datetime.max.time(), tzinfo=tzinfo)
            start = end + td
        self._gt_value = start
        self._gt_operand = ">="
        self._lt_value = end
        self._lt_operand = "<="
        return self._parent_obj


class NumberQuery(Query):
    _min_value = None
    _max_value = None
    _is_int = False

    def equals(self, value):
        return super().equals(value)

    @classmethod
    def init_with_limits(cls, field_name, parent_obj: QueryBlock, min_value=None, max_value=None, is_int=False):
        c = NumberQuery(field_name, parent_obj)
        c._min_value = min_value
        c._max_value = max_value
        c._is_int = is_int
        return c

    def _greater_check(self, value):
        super(NumberQuery, self)._greater_check(value)
        self._check_range(value)

    def _less_check(self, value):
        super(NumberQuery, self)._less_check(value)
        self._check_range(value)

    def _check_range(self, value):
        if self._min_value is not None and value < self._min_value:
            raise ValueError(f"setting value of {value}, "
                             f"can't be less than min value of {self._min_value} for {self._field_name}")
        if self._max_value is not None and value > self._max_value:
            raise ValueError(f"setting value of {value}, "
                             f"can't be greater than max value of {self._max_value} for {self._field_name}")

    def _check(self, value):
        if self._is_int and not isinstance(value, int) and math.floor(value) != value:
            raise ValueError(f"for integer type, must use ints. {value} is not an int")


class SpatialQuery(QueryBase):
    _geometry = None

    def intersects(self, geometry: BaseGeometry) -> QueryBlock:
        self._geometry = geometry
        return self._parent_obj

    def build_query(self):
        if self._geometry is None:
            return None

        return {
            "op": "s_intersects",
            "args": [
                self.property_obj,
                self._geometry.__geo_interface__
            ]
        }


class Extension:
    def __init__(self, query_block: QueryBlock):
        self._filter_expressions: list[QueryTuple] = []

    def build_query(self):
        properties = list(vars(self).values())
        args = [x.build_query() for x in properties if isinstance(x, QueryBase) and x.build_query() is not None]
        for query_filter in self._filter_expressions:
            args.append(query_filter.build_query())

        if len(args) == 0:
            return []
        return args


class CommonName(Enum):
    pan = "pan"
    coastal = "coastal"
    blue = "blue"
    green = "green"
    green05 = "green05"
    yellow = "yellow"
    red = "red"
    rededge = "rededge"
    rededge071 = "rededge071"
    rededge075 = "rededge075"
    rededge078 = "rededge078"
    nir = "nir"
    nir08 = "nir08"
    nir09 = "nir09"
    cirrus = "cirrus"
    swir16 = "swir16"
    swir22 = "swir22"
    lwir = "lwir"
    lwir11 = "lwir11"
    lwir12 = "lwir12"


class CommonNameQuery(EnumQuery):
    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBlock, enum_fields: list[str]):
        o = CommonNameQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: CommonName) -> QueryBlock:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def in_set(self, values: list[CommonName]) -> QueryBlock:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj


class EOExtension(Extension):
    """
    STAC EO Extension for STAC Items and STAC Collections.
    """
    def __init__(self, query_block: QueryBlock):
        super().__init__(query_block)
        self.center_wavelength = NumberQuery.init_with_limits("eo:center_wavelength", query_block, min_value=None, max_value=None)
        self.cloud_cover = NumberQuery.init_with_limits("eo:cloud_cover", query_block, min_value=0, max_value=100)
        self.common_name = CommonNameQuery.init_enums("eo:common_name", query_block, [x.value for x in CommonName])
        self.full_width_half_max = NumberQuery.init_with_limits("eo:full_width_half_max", query_block, min_value=None, max_value=None)
        self.snow_cover = NumberQuery.init_with_limits("eo:snow_cover", query_block, min_value=0, max_value=100)
        self.solar_illumination = NumberQuery.init_with_limits("eo:solar_illumination", query_block, min_value=0, max_value=None)


class FrequencyBand(Enum):
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


class ObservationDirection(Enum):
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


class SARExtension(Extension):
    """
    STAC SAR Extension to a STAC Item
    """
    def __init__(self, query_block: QueryBlock):
        super().__init__(query_block)
        self.center_frequency = NumberQuery.init_with_limits("sar:center_frequency", query_block, min_value=None, max_value=None)
        self.frequency_band = FrequencyBandQuery.init_enums("sar:frequency_band", query_block, [x.value for x in FrequencyBand])
        self.instrument_mode = StringQuery("sar:instrument_mode", query_block)
        self.looks_azimuth = NumberQuery.init_with_limits("sar:looks_azimuth", query_block, min_value=0, max_value=None, is_int=True)
        self.looks_equivalent_number = NumberQuery.init_with_limits("sar:looks_equivalent_number", query_block, min_value=0, max_value=None)
        self.looks_range = NumberQuery.init_with_limits("sar:looks_range", query_block, min_value=0, max_value=None, is_int=True)
        self.observation_direction = ObservationDirectionQuery.init_enums("sar:observation_direction", query_block, [x.value for x in ObservationDirection])
        self.pixel_spacing_azimuth = NumberQuery.init_with_limits("sar:pixel_spacing_azimuth", query_block, min_value=0, max_value=None)
        self.pixel_spacing_range = NumberQuery.init_with_limits("sar:pixel_spacing_range", query_block, min_value=0, max_value=None)
        self.product_type = StringQuery("sar:product_type", query_block)
        self.resolution_azimuth = NumberQuery.init_with_limits("sar:resolution_azimuth", query_block, min_value=0, max_value=None)
        self.resolution_range = NumberQuery.init_with_limits("sar:resolution_range", query_block, min_value=0, max_value=None)


class ViewExtension(Extension):
    """
    STAC View Geometry Extension for STAC Items and STAC Collections.
    """
    def __init__(self, query_block: QueryBlock):
        super().__init__(query_block)
        self.azimuth = NumberQuery.init_with_limits("view:azimuth", query_block, min_value=0, max_value=360)
        self.incidence_angle = NumberQuery.init_with_limits("view:incidence_angle", query_block, min_value=0, max_value=90)
        self.off_nadir = NumberQuery.init_with_limits("view:off_nadir", query_block, min_value=0, max_value=90)
        self.sun_azimuth = NumberQuery.init_with_limits("view:sun_azimuth", query_block, min_value=0, max_value=360)
        self.sun_elevation = NumberQuery.init_with_limits("view:sun_elevation", query_block, min_value=-90, max_value=90)


class OrbitState(Enum):
    ascending = "ascending"
    descending = "descending"
    geostationary = "geostationary"


class OrbitStateQuery(EnumQuery):
    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBlock, enum_fields: list[str]):
        o = OrbitStateQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: OrbitState) -> QueryBlock:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def in_set(self, values: list[OrbitState]) -> QueryBlock:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj


class SatExtension(Extension):
    """
    STAC Sat Extension to a STAC Item.
    """
    def __init__(self, query_block: QueryBlock):
        super().__init__(query_block)
        self.absolute_orbit = NumberQuery.init_with_limits("sat:absolute_orbit", query_block, min_value=1, max_value=None, is_int=True)
        self.anx_datetime = DateQuery("field_name", query_block)
        self.orbit_state = OrbitStateQuery.init_enums("sat:orbit_state", query_block, [x.value for x in OrbitState])
        self.platform_international_designator = StringQuery("sat:platform_international_designator", query_block)
        self.relative_orbit = NumberQuery.init_with_limits("sat:relative_orbit", query_block, min_value=1, max_value=None, is_int=True)


class QueryBlock:
    def __init__(self):
        self._filter_expressions: list[QueryTuple] = []
        self.datetime = DateQuery("datetime", self)
        self.id = StringQuery("id", self)
        self.geometry = SpatialQuery("geometry", self)
        self.created = DateQuery("created", self)
        self.updated = DateQuery("updated", self)
        self.start_datetime = DateQuery("start_datetime", self)
        self.end_datetime = DateQuery("end_datetime", self)
        self.platform = StringQuery("platform", self)
        self.constellation = StringQuery("constellation", self)
        self.mission = StringQuery("mission", self)
        self.gsd = NumberQuery.init_with_limits("gsd", self, min_value=0)
        self.eo = EOExtension(self)
        self.sar = SARExtension(self)
        self.view = ViewExtension(self)
        self.sat = SatExtension(self)

    def build_query(self, top_level_is_or=False):
        properties = list(vars(self).values())
        args = [x.build_query() for x in properties if isinstance(x, QueryBase) and x.build_query() is not None]
        for query_filter in self._filter_expressions:
            args.append(query_filter.build_query())

        for p in properties:
            if isinstance(p, Extension):
                args.extend(p.build_query())

        if len(args) == 0:
            return None
        top_level_op = "and"
        if top_level_is_or:
            top_level_op = "or"
        return {
            "filter-lang": "cql2-json",
            "filter": {
                "op": top_level_op,
                "args": args}}

    def filter(self, *column_expression):
        query_tuple = column_expression[0]
        self._filter_expressions.append(query_tuple)


def filter_grouping(*column_expression):
    filter_tuple = FilterTuple(column_expression[0].left, column_expression[0].op, column_expression[0].right)
    return filter_tuple

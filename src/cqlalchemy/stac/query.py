# This file is generated with version 0.1.0 of cqlalchemy https://github.com/davidraleigh/cqlalchemy
#
# extensions included:
# https://planetlabs.github.io/stac-extension/v1.0.0-beta.3/schema.json#
# https://stac-extensions.github.io/eo/v2.0.0/schema.json#
# https://stac-extensions.github.io/landsat/v2.0.0/schema.json
# https://stac-extensions.github.io/mlm/v1.4.0/schema.json
# https://stac-extensions.github.io/projection/v2.0.0/schema.json
# https://stac-extensions.github.io/sar/v1.2.0/schema.json
# https://stac-extensions.github.io/sat/v1.1.0/schema.json
# https://stac-extensions.github.io/view/v1.0.0/schema.json#
# https://umbra-space.github.io/umbra-stac-extension/json-schema/v1.0.0/schema.json#
#
# ignored fields are:
# None
#
# unique Enum classes generated:
# True
#
# generated on 2025-06-09

from __future__ import annotations

import json
import math
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from json import JSONEncoder
from typing import Optional, Union

import shapely
from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry


class _DateTimeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()


class _QueryTuple:
    def __init__(self, left, op: str, right):
        self.left = left
        self.op = op
        self.right = right

    def __or__(self, other):
        value = _QueryTuple(self, "|", other)
        if value.check_parents(bad_op="&"):
            raise ValueError("can't mix '&' and '|' in `filter` function. must be all 'or', "
                             "or all 'and' (except inside of the 'filter_grouping' function)")
        return value

    def __and__(self, other):
        value = _QueryTuple(self, "&", other)
        if value.check_parents(bad_op="|"):
            raise ValueError("can't mix '&' and '|' in `filter` function. must be all 'or', "
                             "or all 'and' (except inside of the 'filter_grouping' function)")
        return value

    def check_parents(self, bad_op):
        if isinstance(self.left, _QueryBase):
            return False

        if isinstance(self.left, _FilterTuple):
            if self.right.check_parents(bad_op):
                return True
            return False
        if isinstance(self.right, _FilterTuple):
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
    def _recurse_build_query(query_tuple: _QueryTuple, filter_query: dict):
        if isinstance(query_tuple.left, _QueryBase):
            filter_query["args"].append({"op": query_tuple.op,
                                         "args": [query_tuple.left.property_obj, query_tuple.right]})
        elif isinstance(query_tuple.left, _FilterTuple):
            filter_query["args"].append(query_tuple.left._build_query())
            _QueryTuple._recurse_build_query(query_tuple.right, filter_query)
        elif isinstance(query_tuple.right, _FilterTuple):
            filter_query["args"].append(query_tuple.right._build_query())
            _QueryTuple._recurse_build_query(query_tuple.left, filter_query)
        else:
            _QueryTuple._recurse_build_query(query_tuple.left, filter_query)
            _QueryTuple._recurse_build_query(query_tuple.right, filter_query)
        return filter_query

    def _build_query(self):
        filter_query = {"op": "and", "args": []}
        filter_query = _QueryTuple._recurse_build_query(self, filter_query)
        if self.op == "|":
            filter_query["op"] = "or"
        return filter_query


class _FilterTuple(_QueryTuple):
    pass


class _QueryBase:
    def __init__(self, field_name, parent_obj: QueryBuilder):
        self._field_name = field_name
        self._parent_obj = parent_obj

    def sort_by_asc(self):
        self._parent_obj._sort_by_field = self._field_name
        self._parent_obj._sort_by_direction = "asc"

    def sort_by_desc(self):
        self._parent_obj._sort_by_field = self._field_name
        self._parent_obj._sort_by_direction = "desc"

    def _build_query(self):
        pass

    def __eq__(self, other):
        # TODO, check for None and implement an is null
        return _QueryTuple(self, "=", other)

    def __ne__(self, other):
        # TODO, check for None and implement an is null
        return _QueryTuple(self, "!=", other)

    def __gt__(self, other):
        self._greater_check(other)
        return _QueryTuple(self, ">", other)

    def __ge__(self, other):
        self._greater_check(other)
        return _QueryTuple(self, ">=", other)

    def __lt__(self, other):
        self._less_check(other)
        return _QueryTuple(self, "<", other)

    def __le__(self, other):
        self._less_check(other)
        return _QueryTuple(self, "<=", other)

    @property
    def property_obj(self):
        return {"property": self._field_name}

    def _greater_check(self, value):
        pass

    def _less_check(self, value):
        pass

    def _check(self, value):
        pass

    def _clear_values(self):
        pass


class _BooleanQuery(_QueryBase):
    _eq_value = None
    _is_null = None

    def _clear_values(self):
        self._is_null = None
        self._eq_value = None

    def equals(self, value: bool) -> QueryBuilder:
        """
        for the field, query for all items where it's boolean value equals this input

        Args:
            value (bool): equality check for the field.

        Returns:
            QueryBuilder: query builder for additional queries to add
        """
        self._clear_values()
        self._eq_value = value
        return self._parent_obj

    def is_null(self) -> QueryBuilder:
        """
        for the field, query for all items where this field is null

        Returns:
            QueryBuilder: query builder for additional queries to add
        """
        self._clear_values()
        self._is_null = True
        return self._parent_obj

    def _build_query(self):
        if self._eq_value is not None:
            return {
                "op": "=",
                "args": [self.property_obj, self._eq_value]
            }
        elif self._is_null is not None and self._is_null is True:
            return {
                "op": "isNull",
                "args": [self.property_obj]
            }
        return None


class _NullCheck(_QueryBase):
    _is_null = None

    def is_null(self) -> QueryBuilder:
        """
        for the field, query for all items where this field is null

        Returns:
            QueryBuilder: query builder for additional queries to add
        """
        self._clear_values()
        self._is_null = True
        return self._parent_obj

    def _build_query(self):
        if self._is_null is not None and self._is_null is True:
            return {
                "op": "isNull",
                "args": [self.property_obj]
            }
        return None


class _BaseString(_QueryBase):
    _eq_value = None
    _ne_value = None
    _in_values = None
    _not_in_values = None
    _like_value = None
    _is_null = None

    def _clear_values(self):
        self._is_null = None
        self._eq_value = None
        self._ne_value = None
        self._in_values = None
        self._not_in_values = None
        self._like_value = None

    def is_null(self) -> QueryBuilder:
        """
        for the field, query for all items where this field is null

        Returns:
            QueryBuilder: query builder for additional queries to add
        """
        self._clear_values()
        self._is_null = True
        return self._parent_obj

    def _build_query(self):
        if self._eq_value is not None:
            return {
                "op": "=",
                "args": [self.property_obj, self._eq_value]
            }
        elif self._ne_value is not None:
            return {
                "op": "!=",
                "args": [self.property_obj, self._ne_value]
            }
        elif self._in_values is not None and len(self._in_values) > 0:
            return {
                "op": "in",
                "args": [
                    self.property_obj,
                    self._in_values
                ]
            }
        elif self._not_in_values is not None and len(self._not_in_values) > 0:
            return {
                "op": "not",
                "args": [
                    {
                        "op": "in",
                        "args": [
                            self.property_obj,
                            self._not_in_values
                        ]
                    }
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
        elif self._is_null is not None and self._is_null is True:
            return {
                "op": "isNull",
                "args": [self.property_obj]
            }
        return None


class _EnumQuery(_BaseString):
    _enum_values: set[str] = set()

    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBuilder, enum_fields: list[str]):
        c = _EnumQuery(field_name, parent_obj)
        c._enum_values = set(enum_fields)
        if len(c._enum_values) <= 1:
            raise ValueError(f"enum_fields must have 2 or more unique values. fields are {enum_fields}")
        return c

    def _check(self, values: list[str]):
        self._clear_values()
        if not set(values).issubset(self._enum_values):
            raise ValueError("")


class _StringQuery(_BaseString):
    def equals(self, value: str) -> QueryBuilder:
        """
        for the field, query for all items where it's string value equals this input

        Args:
            value (str): equality check for the field.

        Returns:
            QueryBuilder: query builder for additional queries to add
        """
        self._clear_values()
        self._eq_value = self._adjust_enum(value)
        return self._parent_obj

    def not_equals(self, value: str) -> QueryBuilder:
        """
        for the field, query for all items where it's string value does not equal this input

        Args:
            value (str): non-equality check for the field.

        Returns:
            QueryBuilder: query builder for additional queries to add
        """
        self._clear_values()
        self._ne_value = self._adjust_enum(value)
        return self._parent_obj

    def in_set(self, values: list[str]) -> QueryBuilder:
        """
        for the values input, create an in_set query for this field

        Args:
            values (list[str]): for the values input, create an in_set query for this field.

        Returns:
            QueryBuilder: query builder for additional queries to add
        """
        self._clear_values()
        self._in_values = [self._adjust_enum(x) for x in values]
        return self._parent_obj

    def not_in_set(self, values: list[str]) -> QueryBuilder:
        """
        for the values input, create an not_in_set query for this field

        Args:
            values (list[str]): for the values input, create an not_in_set query for this field.

        Returns:
            QueryBuilder: query builder for additional queries to add
        """
        self._clear_values()
        self._not_in_values = [self._adjust_enum(x) for x in values]
        return self._parent_obj

    def like(self, value: str) -> QueryBuilder:
        """
        for the value input, create a like query for this field. Requires using the '%' operator within the value string for wildcard checking

        Args:
            value (str): for the value input, create a like query for this field.

        Returns:
            QueryBuilder: query builder for additional queries to add
        """
        self._clear_values()
        self._like_value = self._adjust_enum(value)
        return self._parent_obj

    def _clear_values(self):
        self._in_values = None
        self._not_in_values = None
        self._eq_value = None
        self._ne_value = None
        self._like_value = None

    @staticmethod
    def _adjust_enum(value):
        if isinstance(value, Enum):
            return value.value
        return str(value)


class _Query(_QueryBase):
    _gt_value = None
    _gt_operand = None
    _lt_value = None
    _lt_operand = None
    _eq_value = None
    _ne_value = None
    _is_null = None

    def _build_query(self):
        if self._eq_value is not None:
            return {
                "op": "=",
                "args": [self.property_obj, self._eq_value]
            }
        elif self._is_null is not None and self._is_null is True:
            return {
                "op": "isNull",
                "args": [self.property_obj]
            }
        elif self._gt_value is None and self._lt_value is None:
            if self._ne_value is None:
                return None
            return {
                "op": "!=",
                "args": [self.property_obj, self._ne_value]
            }

        gt_query = {
            "op": self._gt_operand,
            "args": [self.property_obj, self._gt_value]
        }
        lt_query = {
            "op": self._lt_operand,
            "args": [self.property_obj, self._lt_value]
        }
        ne_query = {
            "op": "!=",
            "args": [self.property_obj, self._ne_value]
        }
        range_query = None
        if self._gt_value is not None and self._lt_value is None:
            if self._ne_value is None:
                return gt_query
            range_query = {
                "op": "and",
                "args": [
                    gt_query
                ]
            }
        elif self._lt_value is not None and self._gt_value is None:
            if self._ne_value is None:
                return lt_query
            range_query = {
                "op": "and",
                "args": [
                    lt_query
                ]
            }
        elif self._gt_value is not None and self._lt_value is not None and self._gt_value < self._lt_value:
            range_query = {
                "op": "and",
                "args": [
                    gt_query, lt_query
                ]
            }
        if range_query is not None:
            if self._ne_value is not None:
                range_query["args"].append(ne_query)
            return range_query

        if self._gt_value is not None and self._lt_value is not None and self._gt_value > self._lt_value:
            range_query = {
                "op": "or",
                "args": [
                    gt_query, lt_query
                ]
            }
            if self._ne_value is not None:
                range_query = {
                    "op": "and",
                    "args": [
                        range_query, ne_query
                    ]
                }
        return range_query

    def equals(self, value) -> QueryBuilder:
        """
        for the field, query for all items where it's value equals this input

        Args:
            value: equality check for the field.

        Returns:
            QueryBuilder: query builder for additional queries to add
        """
        self._check(value)
        self._clear_values()
        self._eq_value = value
        return self._parent_obj

    def not_equals(self, value) -> QueryBuilder:
        """
        for the field, query for all items where it's value does not equal this input

        Args:
            value: inequality check for the field.

        Returns:
            QueryBuilder: query builder for additional queries to add
        """
        self._check(value)
        self._eq_value = None
        self._is_null = None
        self._ne_value = value
        return self._parent_obj

    def gt(self, value) -> QueryBuilder:
        """
        for the field, query for all items where it's value is greater than this input

        Args:
            value: value for greater than check for the field.

        Returns:
            QueryBuilder: query builder for additional queries to add
        """
        self._check(value)
        self._greater_check(value)
        self._eq_value = None
        self._is_null = None
        self._gt_value = value
        self._gt_operand = ">"
        return self._parent_obj

    def gte(self, value) -> QueryBuilder:
        """
        for the field, query for all items where it's value is greater than or equal to this input

        Args:
            value: value for greater than or equal to check for the field.

        Returns:
            QueryBuilder: query builder for additional queries to add
        """
        self._check(value)
        self._greater_check(value)
        self._eq_value = None
        self._is_null = None
        self._gt_value = value
        self._gt_operand = ">="
        return self._parent_obj

    def lt(self, value) -> QueryBuilder:
        """
        for the field, query for all items where it's value is less than this input

        Args:
            value: value for less than check for the field.

        Returns:
            QueryBuilder: query builder for additional queries to add
        """
        self._check(value)
        self._less_check(value)
        self._eq_value = None
        self._is_null = None
        self._lt_value = value
        self._lt_operand = "<"
        return self._parent_obj

    def lte(self, value) -> QueryBuilder:
        """
        for the field, query for all items where it's value is less than or equal to this input

        Args:
            value: value for less than or equal to check for the field.

        Returns:
            QueryBuilder: query builder for additional queries to add
        """
        self._check(value)
        self._less_check(value)
        self._eq_value = None
        self._is_null = None
        self._lt_value = value
        self._lt_operand = "<="
        return self._parent_obj

    def is_null(self) -> QueryBuilder:
        """
        for the field, query for all items where this field is null

        Returns:
            QueryBuilder: query builder for additional queries to add
        """
        self._clear_values()
        self._is_null = True
        return self._parent_obj

    def _clear_values(self):
        self._gt_value = None
        self._gt_operand = None
        self._lt_value = None
        self._lt_operand = None
        self._eq_value = None
        self._ne_value = None
        self._is_null = None


class _DateQuery(_Query):
    def equals(self, value: date, tzinfo=timezone.utc) -> QueryBuilder:
        """
        for the field, query for all items where it's date equals this input

        Args:
            value: equality check for the field.

        Returns:
            QueryBuilder: query builder for additional queries to add
        """
        self._check(value)
        if isinstance(value, datetime):
            self._eq_value = value
        elif isinstance(value, date):
            start = datetime.combine(value, datetime.min.time(), tzinfo=tzinfo)
            end = datetime.combine(value, datetime.max.time(), tzinfo=tzinfo)
            self._gt_value = start
            self._gt_operand = ">="
            self._lt_value = end
            self._lt_operand = "<="
        else:
            self._eq_value = value

        return self._parent_obj

    def not_equals(self, value: date, tzinfo=timezone.utc) -> QueryBuilder:
        """
        for the field, query for all items where it's date equals this input

        Args:
            value: equality check for the field.

        Returns:
            QueryBuilder: query builder for additional queries to add
        """
        self._check(value)
        if isinstance(value, datetime):
            self._ne_value = value
        elif isinstance(value, date):
            start = datetime.combine(value, datetime.min.time(), tzinfo=tzinfo)
            end = datetime.combine(value, datetime.max.time(), tzinfo=tzinfo)
            self._gt_value = end
            self._gt_operand = ">="
            self._lt_value = start
            self._lt_operand = "<="
        else:
            self._ne_value = value

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

    def _check(self, value):
        if isinstance(value, datetime):
            if value.tzinfo is None:
                raise ValueError(f"datetime {value} does not have timezone set.")


class _NumberQuery(_Query):
    _min_value = None
    _max_value = None
    _is_int = False

    def equals(self, value):
        return super().equals(value)

    @classmethod
    def init_with_limits(cls, field_name, parent_obj: QueryBuilder, min_value=None, max_value=None, is_int=False):
        c = _NumberQuery(field_name, parent_obj)
        c._min_value = min_value
        c._max_value = max_value
        c._is_int = is_int
        return c

    def _greater_check(self, value):
        super(_NumberQuery, self)._greater_check(value)
        self._check_range(value)

    def _less_check(self, value):
        super(_NumberQuery, self)._less_check(value)
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
        self._check_range(value)


class _SpatialQuery(_QueryBase):
    _geometry = None
    _is_null = None

    def intersects(self, geometry: Union[BaseGeometry, dict]) -> QueryBuilder:
        if isinstance(geometry, BaseGeometry):
            self._geometry = geometry.__geo_interface__
        elif isinstance(geometry, dict):
            # check to make sure geometry is correctly formatted
            try:
                # check for polygons that aren't closed
                shapely.from_geojson(json.dumps(geometry))
            except shapely.GEOSException as ge:
                if "Expected two coordinates found more than two" not in str(ge):
                    raise
                else:
                    # check for geometries with x, y, and z defined
                    shape(geometry)
            self._geometry = geometry
        else:
            raise ValueError("input must be shapely geometry or a geojson formatted dictionary")
        self._is_null = None
        return self._parent_obj

    def is_null(self) -> QueryBuilder:
        """
        for the field, query for all items where this field is null

        Returns:
            QueryBuilder: query builder for additional queries to add
        """
        self._geometry = None
        self._is_null = True
        return self._parent_obj

    def _build_query(self):
        if self._is_null is not None:
            return {
                "op": "isNull",
                "args": [self.property_obj]
            }
        if self._geometry is None:
            return None

        return {
            "op": "s_intersects",
            "args": [
                self.property_obj,
                self._geometry
            ]
        }


class _Extension:
    def __init__(self, query_block: QueryBuilder):
        self._filter_expressions: list[_QueryTuple] = []

    def _build_query(self):
        properties = list(vars(self).values())
        args = [x._build_query() for x in properties if isinstance(x, _QueryBase) and x._build_query() is not None]
        for query_filter in self._filter_expressions:
            args.append(query_filter._build_query())

        if len(args) == 0:
            return []
        return args


class PLItemTypeEnum(str, Enum):
    """
    PL Item Type Enum
    """

    Landsat8L1G = "Landsat8L1G"
    PSOrthoTile = "PSOrthoTile"
    PSScene = "PSScene"
    PSScene3Band = "PSScene3Band"
    PSScene4Band = "PSScene4Band"
    MOD09GA = "MOD09GA"
    MOD09GQ = "MOD09GQ"
    MYD09GA = "MYD09GA"
    MYD09GQ = "MYD09GQ"
    REOrthoTile = "REOrthoTile"
    REScene = "REScene"
    Sentinel1 = "Sentinel1"
    Sentinel2L1C = "Sentinel2L1C"
    SkySatCollect = "SkySatCollect"
    SkySatScene = "SkySatScene"
    SkySatVideo = "SkySatVideo"


class _PLItemTypeEnumQuery(_EnumQuery):
    """
    PL Item Type Enum Query Interface
    """

    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBuilder, enum_fields: list[str]):
        o = _PLItemTypeEnumQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: PLItemTypeEnum) -> QueryBuilder:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def not_equals(self, value: PLItemTypeEnum) -> QueryBuilder:
        self._check([value.value])
        self._ne_value = value.value
        return self._parent_obj

    def in_set(self, values: list[PLItemTypeEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj

    def not_in_set(self, values: list[PLItemTypeEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._not_in_values = extracted
        return self._parent_obj

    def Landsat8L1G(self) -> QueryBuilder:
        return self.equals(PLItemTypeEnum.Landsat8L1G)

    def PSOrthoTile(self) -> QueryBuilder:
        return self.equals(PLItemTypeEnum.PSOrthoTile)

    def PSScene(self) -> QueryBuilder:
        return self.equals(PLItemTypeEnum.PSScene)

    def PSScene3Band(self) -> QueryBuilder:
        return self.equals(PLItemTypeEnum.PSScene3Band)

    def PSScene4Band(self) -> QueryBuilder:
        return self.equals(PLItemTypeEnum.PSScene4Band)

    def MOD09GA(self) -> QueryBuilder:
        return self.equals(PLItemTypeEnum.MOD09GA)

    def MOD09GQ(self) -> QueryBuilder:
        return self.equals(PLItemTypeEnum.MOD09GQ)

    def MYD09GA(self) -> QueryBuilder:
        return self.equals(PLItemTypeEnum.MYD09GA)

    def MYD09GQ(self) -> QueryBuilder:
        return self.equals(PLItemTypeEnum.MYD09GQ)

    def REOrthoTile(self) -> QueryBuilder:
        return self.equals(PLItemTypeEnum.REOrthoTile)

    def REScene(self) -> QueryBuilder:
        return self.equals(PLItemTypeEnum.REScene)

    def Sentinel1(self) -> QueryBuilder:
        return self.equals(PLItemTypeEnum.Sentinel1)

    def Sentinel2L1C(self) -> QueryBuilder:
        return self.equals(PLItemTypeEnum.Sentinel2L1C)

    def SkySatCollect(self) -> QueryBuilder:
        return self.equals(PLItemTypeEnum.SkySatCollect)

    def SkySatScene(self) -> QueryBuilder:
        return self.equals(PLItemTypeEnum.SkySatScene)

    def SkySatVideo(self) -> QueryBuilder:
        return self.equals(PLItemTypeEnum.SkySatVideo)


class PLPublishingStageEnum(str, Enum):
    """
    PL Publishing Stage Enum
    """

    preview = "preview"
    standard = "standard"
    finalized = "finalized"


class _PLPublishingStageEnumQuery(_EnumQuery):
    """
    PL Publishing Stage Enum Query Interface
    """

    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBuilder, enum_fields: list[str]):
        o = _PLPublishingStageEnumQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: PLPublishingStageEnum) -> QueryBuilder:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def not_equals(self, value: PLPublishingStageEnum) -> QueryBuilder:
        self._check([value.value])
        self._ne_value = value.value
        return self._parent_obj

    def in_set(self, values: list[PLPublishingStageEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj

    def not_in_set(self, values: list[PLPublishingStageEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._not_in_values = extracted
        return self._parent_obj

    def preview(self) -> QueryBuilder:
        return self.equals(PLPublishingStageEnum.preview)

    def standard(self) -> QueryBuilder:
        return self.equals(PLPublishingStageEnum.standard)

    def finalized(self) -> QueryBuilder:
        return self.equals(PLPublishingStageEnum.finalized)


class PLQualityCategoryEnum(str, Enum):
    """
    PL Quality Category Enum
    """

    standard = "standard"
    test = "test"


class _PLQualityCategoryEnumQuery(_EnumQuery):
    """
    PL Quality Category Enum Query Interface
    """

    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBuilder, enum_fields: list[str]):
        o = _PLQualityCategoryEnumQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: PLQualityCategoryEnum) -> QueryBuilder:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def not_equals(self, value: PLQualityCategoryEnum) -> QueryBuilder:
        self._check([value.value])
        self._ne_value = value.value
        return self._parent_obj

    def in_set(self, values: list[PLQualityCategoryEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj

    def not_in_set(self, values: list[PLQualityCategoryEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._not_in_values = extracted
        return self._parent_obj

    def standard(self) -> QueryBuilder:
        return self.equals(PLQualityCategoryEnum.standard)

    def test(self) -> QueryBuilder:
        return self.equals(PLQualityCategoryEnum.test)


class _PlExtension(_Extension):
    """
    STAC Planet Labs Extension for STAC Items and STAC Collections. Validates the fields, doesn't require specific assets to be present.

    ...

    Attributes
    ----------
    black_fill: _NumberQuery
        number query interface for searching items by the pl:black_fill field where the minimum value is 0 and the max value is 100. Float input.
    clear_percent: _NumberQuery
        number query interface for searching items by the pl:clear_percent field where the minimum value is 0 and the max value is 100. Float input.
    grid_cell : _StringQuery
        string query interface for searching items by the pl:grid_cell field
    ground_control : _BooleanQuery
        enum query interface for searching items by the pl:ground_control field
    ground_control_ratio: _NumberQuery
        number query interface for searching items by the pl:ground_control_ratio field where the minimum value is 0 and the max value is 1. Float input.
    item_type : _PLItemTypeEnumQuery
        enum query interface for searching items by the pl:item_type field
    pixel_resolution: _NumberQuery
        number query interface for searching items by the pl:pixel_resolution field. Float input.
    publishing_stage : _PLPublishingStageEnumQuery
        enum query interface for searching items by the pl:publishing_stage field
    quality_category : _PLQualityCategoryEnumQuery
        enum query interface for searching items by the pl:quality_category field
    strip_id : _StringQuery
        string query interface for searching items by the pl:strip_id field
    """
    def __init__(self, query_block: QueryBuilder):
        super().__init__(query_block)
        self.black_fill = _NumberQuery.init_with_limits("pl:black_fill", query_block, min_value=0, max_value=100, is_int=False)
        self.clear_percent = _NumberQuery.init_with_limits("pl:clear_percent", query_block, min_value=0, max_value=100, is_int=False)
        self.grid_cell = _StringQuery("pl:grid_cell", query_block)
        self.ground_control = _BooleanQuery("pl:ground_control", query_block)
        self.ground_control_ratio = _NumberQuery.init_with_limits("pl:ground_control_ratio", query_block, min_value=0, max_value=1, is_int=False)
        self.item_type = _PLItemTypeEnumQuery.init_enums("pl:item_type", query_block, [x.value for x in PLItemTypeEnum])
        self.pixel_resolution = _NumberQuery.init_with_limits("pl:pixel_resolution", query_block, min_value=None, max_value=None, is_int=False)
        self.publishing_stage = _PLPublishingStageEnumQuery.init_enums("pl:publishing_stage", query_block, [x.value for x in PLPublishingStageEnum])
        self.quality_category = _PLQualityCategoryEnumQuery.init_enums("pl:quality_category", query_block, [x.value for x in PLQualityCategoryEnum])
        self.strip_id = _StringQuery("pl:strip_id", query_block)


class EOCommonNameEnum(str, Enum):
    """
    EO Common Name Enum
    """

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


class _EOCommonNameEnumQuery(_EnumQuery):
    """
    EO Common Name Enum Query Interface
    Common Name of the band
    """

    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBuilder, enum_fields: list[str]):
        o = _EOCommonNameEnumQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: EOCommonNameEnum) -> QueryBuilder:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def not_equals(self, value: EOCommonNameEnum) -> QueryBuilder:
        self._check([value.value])
        self._ne_value = value.value
        return self._parent_obj

    def in_set(self, values: list[EOCommonNameEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj

    def not_in_set(self, values: list[EOCommonNameEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._not_in_values = extracted
        return self._parent_obj

    def pan(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.pan)

    def coastal(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.coastal)

    def blue(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.blue)

    def green(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.green)

    def green05(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.green05)

    def yellow(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.yellow)

    def red(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.red)

    def rededge(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.rededge)

    def rededge071(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.rededge071)

    def rededge075(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.rededge075)

    def rededge078(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.rededge078)

    def nir(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.nir)

    def nir08(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.nir08)

    def nir09(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.nir09)

    def cirrus(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.cirrus)

    def swir16(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.swir16)

    def swir22(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.swir22)

    def lwir(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.lwir)

    def lwir11(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.lwir11)

    def lwir12(self) -> QueryBuilder:
        return self.equals(EOCommonNameEnum.lwir12)


class _EOExtension(_Extension):
    """
    STAC EO Extension for STAC Items and STAC Collections.

    ...

    Attributes
    ----------
    center_wavelength: _NumberQuery
        number query interface for searching items by the eo:center_wavelength field. Float input.
    cloud_cover: _NumberQuery
        number query interface for searching items by the eo:cloud_cover field where the minimum value is 0 and the max value is 100. Float input.
    common_name : _EOCommonNameEnumQuery
        enum query interface for searching items by the eo:common_name field
    full_width_half_max: _NumberQuery
        number query interface for searching items by the eo:full_width_half_max field. Float input.
    snow_cover: _NumberQuery
        number query interface for searching items by the eo:snow_cover field where the minimum value is 0 and the max value is 100. Float input.
    solar_illumination: _NumberQuery
        number query interface for searching items by the eo:solar_illumination field where the minimum value is 0. Float input.
    """
    def __init__(self, query_block: QueryBuilder):
        super().__init__(query_block)
        self.center_wavelength = _NumberQuery.init_with_limits("eo:center_wavelength", query_block, min_value=None, max_value=None, is_int=False)
        self.cloud_cover = _NumberQuery.init_with_limits("eo:cloud_cover", query_block, min_value=0, max_value=100, is_int=False)
        self.common_name = _EOCommonNameEnumQuery.init_enums("eo:common_name", query_block, [x.value for x in EOCommonNameEnum])
        self.full_width_half_max = _NumberQuery.init_with_limits("eo:full_width_half_max", query_block, min_value=None, max_value=None, is_int=False)
        self.snow_cover = _NumberQuery.init_with_limits("eo:snow_cover", query_block, min_value=0, max_value=100, is_int=False)
        self.solar_illumination = _NumberQuery.init_with_limits("eo:solar_illumination", query_block, min_value=0, max_value=None, is_int=False)


class LandsatCollectionCategoryEnum(str, Enum):
    """
    Landsat Collection Category Enum
    """

    A1 = "A1"
    A2 = "A2"
    T1 = "T1"
    T2 = "T2"
    RT = "RT"


class _LandsatCollectionCategoryEnumQuery(_EnumQuery):
    """
    Landsat Collection Category Enum Query Interface
    Collection Category
    """

    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBuilder, enum_fields: list[str]):
        o = _LandsatCollectionCategoryEnumQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: LandsatCollectionCategoryEnum) -> QueryBuilder:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def not_equals(self, value: LandsatCollectionCategoryEnum) -> QueryBuilder:
        self._check([value.value])
        self._ne_value = value.value
        return self._parent_obj

    def in_set(self, values: list[LandsatCollectionCategoryEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj

    def not_in_set(self, values: list[LandsatCollectionCategoryEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._not_in_values = extracted
        return self._parent_obj

    def A1(self) -> QueryBuilder:
        return self.equals(LandsatCollectionCategoryEnum.A1)

    def A2(self) -> QueryBuilder:
        return self.equals(LandsatCollectionCategoryEnum.A2)

    def T1(self) -> QueryBuilder:
        return self.equals(LandsatCollectionCategoryEnum.T1)

    def T2(self) -> QueryBuilder:
        return self.equals(LandsatCollectionCategoryEnum.T2)

    def RT(self) -> QueryBuilder:
        return self.equals(LandsatCollectionCategoryEnum.RT)


class LandsatCorrectionEnum(str, Enum):
    """
    Landsat Correction Enum
    """

    L1TP = "L1TP"
    L1GT = "L1GT"
    L1GS = "L1GS"
    L2SR = "L2SR"
    L2SP = "L2SP"


class _LandsatCorrectionEnumQuery(_EnumQuery):
    """
    Landsat Correction Enum Query Interface
    Product Correction Level
    """

    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBuilder, enum_fields: list[str]):
        o = _LandsatCorrectionEnumQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: LandsatCorrectionEnum) -> QueryBuilder:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def not_equals(self, value: LandsatCorrectionEnum) -> QueryBuilder:
        self._check([value.value])
        self._ne_value = value.value
        return self._parent_obj

    def in_set(self, values: list[LandsatCorrectionEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj

    def not_in_set(self, values: list[LandsatCorrectionEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._not_in_values = extracted
        return self._parent_obj

    def L1TP(self) -> QueryBuilder:
        return self.equals(LandsatCorrectionEnum.L1TP)

    def L1GT(self) -> QueryBuilder:
        return self.equals(LandsatCorrectionEnum.L1GT)

    def L1GS(self) -> QueryBuilder:
        return self.equals(LandsatCorrectionEnum.L1GS)

    def L2SR(self) -> QueryBuilder:
        return self.equals(LandsatCorrectionEnum.L2SR)

    def L2SP(self) -> QueryBuilder:
        return self.equals(LandsatCorrectionEnum.L2SP)


class _LandsatExtension(_Extension):
    """
    Landsat Extension to STAC Items.

    ...

    Attributes
    ----------
    cloud_cover_land: _NumberQuery
        number query interface for searching items by the landsat:cloud_cover_land field where the minimum value is -1 and the max value is 100. Float input.
    collection_category : _LandsatCollectionCategoryEnumQuery
        enum query interface for searching items by the landsat:collection_category field
    collection_number : _StringQuery
        string query interface for searching items by the landsat:collection_number field
    correction : _LandsatCorrectionEnumQuery
        enum query interface for searching items by the landsat:correction field
    product_generated : _DateQuery
        datetime query interface for searching items by the landsat:product_generated field
    scene_id : _StringQuery
        string query interface for searching items by the landsat:scene_id field
    wrs_path : _StringQuery
        string query interface for searching items by the landsat:wrs_path field
    wrs_row : _StringQuery
        string query interface for searching items by the landsat:wrs_row field
    wrs_type : _StringQuery
        string query interface for searching items by the landsat:wrs_type field
    """
    def __init__(self, query_block: QueryBuilder):
        super().__init__(query_block)
        self.cloud_cover_land = _NumberQuery.init_with_limits("landsat:cloud_cover_land", query_block, min_value=-1, max_value=100, is_int=False)
        self.collection_category = _LandsatCollectionCategoryEnumQuery.init_enums("landsat:collection_category", query_block, [x.value for x in LandsatCollectionCategoryEnum])
        self.collection_number = _StringQuery("landsat:collection_number", query_block)
        self.correction = _LandsatCorrectionEnumQuery.init_enums("landsat:correction", query_block, [x.value for x in LandsatCorrectionEnum])
        self.product_generated = _DateQuery("landsat:product_generated", query_block)
        self.scene_id = _StringQuery("landsat:scene_id", query_block)
        self.wrs_path = _StringQuery("landsat:wrs_path", query_block)
        self.wrs_row = _StringQuery("landsat:wrs_row", query_block)
        self.wrs_type = _StringQuery("landsat:wrs_type", query_block)


class MLMAcceleratorEnum(str, Enum):
    """
    MLM Accelerator Enum
    """

    amd64 = "amd64"
    cuda = "cuda"
    xla = "xla"
    amd_rocm = "amd-rocm"
    intel_ipex_cpu = "intel-ipex-cpu"
    intel_ipex_gpu = "intel-ipex-gpu"
    macos_arm = "macos-arm"


class _MLMAcceleratorEnumQuery(_EnumQuery):
    """
    MLM Accelerator Enum Query Interface
    """

    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBuilder, enum_fields: list[str]):
        o = _MLMAcceleratorEnumQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: MLMAcceleratorEnum) -> QueryBuilder:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def not_equals(self, value: MLMAcceleratorEnum) -> QueryBuilder:
        self._check([value.value])
        self._ne_value = value.value
        return self._parent_obj

    def in_set(self, values: list[MLMAcceleratorEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj

    def not_in_set(self, values: list[MLMAcceleratorEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._not_in_values = extracted
        return self._parent_obj

    def amd64(self) -> QueryBuilder:
        return self.equals(MLMAcceleratorEnum.amd64)

    def cuda(self) -> QueryBuilder:
        return self.equals(MLMAcceleratorEnum.cuda)

    def xla(self) -> QueryBuilder:
        return self.equals(MLMAcceleratorEnum.xla)

    def amd_rocm(self) -> QueryBuilder:
        return self.equals(MLMAcceleratorEnum.amd_rocm)

    def intel_ipex_cpu(self) -> QueryBuilder:
        return self.equals(MLMAcceleratorEnum.intel_ipex_cpu)

    def intel_ipex_gpu(self) -> QueryBuilder:
        return self.equals(MLMAcceleratorEnum.intel_ipex_gpu)

    def macos_arm(self) -> QueryBuilder:
        return self.equals(MLMAcceleratorEnum.macos_arm)


class MLMFrameworkEnum(str, Enum):
    """
    MLM Framework Enum
    """

    PyTorch = "PyTorch"
    TensorFlow = "TensorFlow"
    scikit_learn = "scikit-learn"
    Hugging_Face = "Hugging Face"
    Keras = "Keras"
    ONNX = "ONNX"
    rgee = "rgee"
    spatialRF = "spatialRF"
    JAX = "JAX"
    Flax = "Flax"
    MXNet = "MXNet"
    Caffe = "Caffe"
    PyMC = "PyMC"
    Weka = "Weka"
    Paddle = "Paddle"


class _MLMFrameworkEnumQuery(_EnumQuery):
    """
    MLM Framework Enum Query Interface
    Any other framework name to allow extension. Enum names should be preferred when possible to allow better portability.
    """

    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBuilder, enum_fields: list[str]):
        o = _MLMFrameworkEnumQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: MLMFrameworkEnum) -> QueryBuilder:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def not_equals(self, value: MLMFrameworkEnum) -> QueryBuilder:
        self._check([value.value])
        self._ne_value = value.value
        return self._parent_obj

    def in_set(self, values: list[MLMFrameworkEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj

    def not_in_set(self, values: list[MLMFrameworkEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._not_in_values = extracted
        return self._parent_obj

    def PyTorch(self) -> QueryBuilder:
        return self.equals(MLMFrameworkEnum.PyTorch)

    def TensorFlow(self) -> QueryBuilder:
        return self.equals(MLMFrameworkEnum.TensorFlow)

    def scikit_learn(self) -> QueryBuilder:
        return self.equals(MLMFrameworkEnum.scikit_learn)

    def Hugging_Face(self) -> QueryBuilder:
        return self.equals(MLMFrameworkEnum.Hugging_Face)

    def Keras(self) -> QueryBuilder:
        return self.equals(MLMFrameworkEnum.Keras)

    def ONNX(self) -> QueryBuilder:
        return self.equals(MLMFrameworkEnum.ONNX)

    def rgee(self) -> QueryBuilder:
        return self.equals(MLMFrameworkEnum.rgee)

    def spatialRF(self) -> QueryBuilder:
        return self.equals(MLMFrameworkEnum.spatialRF)

    def JAX(self) -> QueryBuilder:
        return self.equals(MLMFrameworkEnum.JAX)

    def Flax(self) -> QueryBuilder:
        return self.equals(MLMFrameworkEnum.Flax)

    def MXNet(self) -> QueryBuilder:
        return self.equals(MLMFrameworkEnum.MXNet)

    def Caffe(self) -> QueryBuilder:
        return self.equals(MLMFrameworkEnum.Caffe)

    def PyMC(self) -> QueryBuilder:
        return self.equals(MLMFrameworkEnum.PyMC)

    def Weka(self) -> QueryBuilder:
        return self.equals(MLMFrameworkEnum.Weka)

    def Paddle(self) -> QueryBuilder:
        return self.equals(MLMFrameworkEnum.Paddle)


class _MLMExtension(_Extension):
    """
    This object represents the metadata for a Machine Learning Model (MLM) used in STAC documents.

    ...

    Attributes
    ----------
    accelerator : _MLMAcceleratorEnumQuery
        enum query interface for searching items by the mlm:accelerator field
    accelerator_constrained : _BooleanQuery
        enum query interface for searching items by the mlm:accelerator_constrained field
    accelerator_count: _NumberQuery
        number query interface for searching items by the mlm:accelerator_count field where the minimum value is 1. Float input.. Integer input.
    accelerator_summary : _StringQuery
        string query interface for searching items by the mlm:accelerator_summary field
    architecture : _StringQuery
        string query interface for searching items by the mlm:architecture field
    artifact_type : _StringQuery
        string query interface for searching items by the mlm:artifact_type field
    batch_size_suggestion: _NumberQuery
        number query interface for searching items by the mlm:batch_size_suggestion field where the minimum value is 0. Float input.. Integer input.
    compile_method : _StringQuery
        string query interface for searching items by the mlm:compile_method field
    framework : _MLMFrameworkEnumQuery
        enum query interface for searching items by the mlm:framework field
    framework_version : _StringQuery
        string query interface for searching items by the mlm:framework_version field
    hyperparameters : _NullCheck
        field can be checked to see if mlm:hyperparameters is null
    input : _NullCheck
        field can be checked to see if mlm:input is null
    memory_size: _NumberQuery
        number query interface for searching items by the mlm:memory_size field where the minimum value is 0. Float input.. Integer input.
    name : _StringQuery
        string query interface for searching items by the mlm:name field
    output : _NullCheck
        field can be checked to see if mlm:output is null
    pretrained : _BooleanQuery
        enum query interface for searching items by the mlm:pretrained field
    pretrained_source : _StringQuery
        string query interface for searching items by the mlm:pretrained_source field
    tasks : _NullCheck
        field can be checked to see if mlm:tasks is null
    total_parameters: _NumberQuery
        number query interface for searching items by the mlm:total_parameters field where the minimum value is 0. Float input.. Integer input.
    """
    def __init__(self, query_block: QueryBuilder):
        super().__init__(query_block)
        self.accelerator = _MLMAcceleratorEnumQuery.init_enums("mlm:accelerator", query_block, [x.value for x in MLMAcceleratorEnum])
        self.accelerator_constrained = _BooleanQuery("mlm:accelerator_constrained", query_block)
        self.accelerator_count = _NumberQuery.init_with_limits("mlm:accelerator_count", query_block, min_value=1, max_value=None, is_int=True)
        self.accelerator_summary = _StringQuery("mlm:accelerator_summary", query_block)
        self.architecture = _StringQuery("mlm:architecture", query_block)
        self.artifact_type = _StringQuery("mlm:artifact_type", query_block)
        self.batch_size_suggestion = _NumberQuery.init_with_limits("mlm:batch_size_suggestion", query_block, min_value=0, max_value=None, is_int=True)
        self.compile_method = _StringQuery("mlm:compile_method", query_block)
        self.framework = _MLMFrameworkEnumQuery.init_enums("mlm:framework", query_block, [x.value for x in MLMFrameworkEnum])
        self.framework_version = _StringQuery("mlm:framework_version", query_block)
        self.hyperparameters = _NullCheck("mlm:hyperparameters", query_block)
        self.input = _NullCheck("mlm:input", query_block)
        self.memory_size = _NumberQuery.init_with_limits("mlm:memory_size", query_block, min_value=0, max_value=None, is_int=True)
        self.name = _StringQuery("mlm:name", query_block)
        self.output = _NullCheck("mlm:output", query_block)
        self.pretrained = _BooleanQuery("mlm:pretrained", query_block)
        self.pretrained_source = _StringQuery("mlm:pretrained_source", query_block)
        self.tasks = _NullCheck("mlm:tasks", query_block)
        self.total_parameters = _NumberQuery.init_with_limits("mlm:total_parameters", query_block, min_value=0, max_value=None, is_int=True)


class _ProjExtension(_Extension):
    """
    STAC Projection Extension for STAC Items.

    ...

    Attributes
    ----------
    bbox : _NullCheck
        field can be checked to see if proj:bbox is null
    centroid : _NullCheck
        field can be checked to see if proj:centroid is null
    code : _StringQuery
        string query interface for searching items by the proj:code field
    geometry : _SpatialQuery
        geometry query interface for searching items by the proj:geometry field
    shape : _NullCheck
        field can be checked to see if proj:shape is null
    transform : _NullCheck
        field can be checked to see if proj:transform is null
    wkt2 : _StringQuery
        string query interface for searching items by the proj:wkt2 field
    """
    def __init__(self, query_block: QueryBuilder):
        super().__init__(query_block)
        self.bbox = _NullCheck("proj:bbox", query_block)
        self.centroid = _NullCheck("proj:centroid", query_block)
        self.code = _StringQuery("proj:code", query_block)
        self.geometry = _SpatialQuery("proj:geometry", query_block)
        self.shape = _NullCheck("proj:shape", query_block)
        self.transform = _NullCheck("proj:transform", query_block)
        self.wkt2 = _StringQuery("proj:wkt2", query_block)


class SARFrequencyBandEnum(str, Enum):
    """
    SAR Frequency Band Enum
    """

    P = "P"
    L = "L"
    S = "S"
    C = "C"
    X = "X"
    Ku = "Ku"
    K = "K"
    Ka = "Ka"


class _SARFrequencyBandEnumQuery(_EnumQuery):
    """
    SAR Frequency Band Enum Query Interface
    Frequency Band
    """

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

    def P(self) -> QueryBuilder:
        return self.equals(SARFrequencyBandEnum.P)

    def L(self) -> QueryBuilder:
        return self.equals(SARFrequencyBandEnum.L)

    def S(self) -> QueryBuilder:
        return self.equals(SARFrequencyBandEnum.S)

    def C(self) -> QueryBuilder:
        return self.equals(SARFrequencyBandEnum.C)

    def X(self) -> QueryBuilder:
        return self.equals(SARFrequencyBandEnum.X)

    def Ku(self) -> QueryBuilder:
        return self.equals(SARFrequencyBandEnum.Ku)

    def K(self) -> QueryBuilder:
        return self.equals(SARFrequencyBandEnum.K)

    def Ka(self) -> QueryBuilder:
        return self.equals(SARFrequencyBandEnum.Ka)


class SARObservationDirectionEnum(str, Enum):
    """
    SAR Observation Direction Enum
    """

    left = "left"
    right = "right"


class _SARObservationDirectionEnumQuery(_EnumQuery):
    """
    SAR Observation Direction Enum Query Interface
    Antenna pointing direction
    """

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


class _SARExtension(_Extension):
    """
    STAC SAR Extension for STAC Items and STAC Collections.

    ...

    Attributes
    ----------
    beam_ids : _NullCheck
        field can be checked to see if sar:beam_ids is null
    center_frequency: _NumberQuery
        number query interface for searching items by the sar:center_frequency field. Float input.
    frequency_band : _SARFrequencyBandEnumQuery
        enum query interface for searching items by the sar:frequency_band field
    instrument_mode : _StringQuery
        string query interface for searching items by the sar:instrument_mode field
    looks_azimuth: _NumberQuery
        number query interface for searching items by the sar:looks_azimuth field where the minimum value is 0. Float input.. Integer input.
    looks_equivalent_number: _NumberQuery
        number query interface for searching items by the sar:looks_equivalent_number field where the minimum value is 0. Float input.
    looks_range: _NumberQuery
        number query interface for searching items by the sar:looks_range field where the minimum value is 0. Float input.. Integer input.
    observation_direction : _SARObservationDirectionEnumQuery
        enum query interface for searching items by the sar:observation_direction field
    pixel_spacing_azimuth: _NumberQuery
        number query interface for searching items by the sar:pixel_spacing_azimuth field where the minimum value is 0. Float input.
    pixel_spacing_range: _NumberQuery
        number query interface for searching items by the sar:pixel_spacing_range field where the minimum value is 0. Float input.
    polarizations : _NullCheck
        field can be checked to see if sar:polarizations is null
    product_type : _StringQuery
        string query interface for searching items by the sar:product_type field
    resolution_azimuth: _NumberQuery
        number query interface for searching items by the sar:resolution_azimuth field where the minimum value is 0. Float input.
    resolution_range: _NumberQuery
        number query interface for searching items by the sar:resolution_range field where the minimum value is 0. Float input.
    """
    def __init__(self, query_block: QueryBuilder):
        super().__init__(query_block)
        self.beam_ids = _NullCheck("sar:beam_ids", query_block)
        self.center_frequency = _NumberQuery.init_with_limits("sar:center_frequency", query_block, min_value=None, max_value=None, is_int=False)
        self.frequency_band = _SARFrequencyBandEnumQuery.init_enums("sar:frequency_band", query_block, [x.value for x in SARFrequencyBandEnum])
        self.instrument_mode = _StringQuery("sar:instrument_mode", query_block)
        self.looks_azimuth = _NumberQuery.init_with_limits("sar:looks_azimuth", query_block, min_value=0, max_value=None, is_int=True)
        self.looks_equivalent_number = _NumberQuery.init_with_limits("sar:looks_equivalent_number", query_block, min_value=0, max_value=None, is_int=False)
        self.looks_range = _NumberQuery.init_with_limits("sar:looks_range", query_block, min_value=0, max_value=None, is_int=True)
        self.observation_direction = _SARObservationDirectionEnumQuery.init_enums("sar:observation_direction", query_block, [x.value for x in SARObservationDirectionEnum])
        self.pixel_spacing_azimuth = _NumberQuery.init_with_limits("sar:pixel_spacing_azimuth", query_block, min_value=0, max_value=None, is_int=False)
        self.pixel_spacing_range = _NumberQuery.init_with_limits("sar:pixel_spacing_range", query_block, min_value=0, max_value=None, is_int=False)
        self.polarizations = _NullCheck("sar:polarizations", query_block)
        self.product_type = _StringQuery("sar:product_type", query_block)
        self.resolution_azimuth = _NumberQuery.init_with_limits("sar:resolution_azimuth", query_block, min_value=0, max_value=None, is_int=False)
        self.resolution_range = _NumberQuery.init_with_limits("sar:resolution_range", query_block, min_value=0, max_value=None, is_int=False)


class SATOrbitStateEnum(str, Enum):
    """
    SAT Orbit State Enum
    """

    ascending = "ascending"
    descending = "descending"
    geostationary = "geostationary"


class _SATOrbitStateEnumQuery(_EnumQuery):
    """
    SAT Orbit State Enum Query Interface
    Orbit State
    """

    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBuilder, enum_fields: list[str]):
        o = _SATOrbitStateEnumQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: SATOrbitStateEnum) -> QueryBuilder:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def not_equals(self, value: SATOrbitStateEnum) -> QueryBuilder:
        self._check([value.value])
        self._ne_value = value.value
        return self._parent_obj

    def in_set(self, values: list[SATOrbitStateEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj

    def not_in_set(self, values: list[SATOrbitStateEnum]) -> QueryBuilder:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._not_in_values = extracted
        return self._parent_obj

    def ascending(self) -> QueryBuilder:
        return self.equals(SATOrbitStateEnum.ascending)

    def descending(self) -> QueryBuilder:
        return self.equals(SATOrbitStateEnum.descending)

    def geostationary(self) -> QueryBuilder:
        return self.equals(SATOrbitStateEnum.geostationary)


class _SatExtension(_Extension):
    """
    STAC Sat Extension to a STAC Item.

    ...

    Attributes
    ----------
    absolute_orbit: _NumberQuery
        number query interface for searching items by the sat:absolute_orbit field where the minimum value is 1. Float input.. Integer input.
    anx_datetime : _DateQuery
        datetime query interface for searching items by the sat:anx_datetime field
    orbit_cycle: _NumberQuery
        number query interface for searching items by the sat:orbit_cycle field where the minimum value is 1. Float input.. Integer input.
    orbit_state : _SATOrbitStateEnumQuery
        enum query interface for searching items by the sat:orbit_state field
    orbit_state_vectors : _NullCheck
        field can be checked to see if sat:orbit_state_vectors is null
    platform_international_designator : _StringQuery
        string query interface for searching items by the sat:platform_international_designator field
    relative_orbit: _NumberQuery
        number query interface for searching items by the sat:relative_orbit field where the minimum value is 1. Float input.. Integer input.
    """
    def __init__(self, query_block: QueryBuilder):
        super().__init__(query_block)
        self.absolute_orbit = _NumberQuery.init_with_limits("sat:absolute_orbit", query_block, min_value=1, max_value=None, is_int=True)
        self.anx_datetime = _DateQuery("sat:anx_datetime", query_block)
        self.orbit_cycle = _NumberQuery.init_with_limits("sat:orbit_cycle", query_block, min_value=1, max_value=None, is_int=True)
        self.orbit_state = _SATOrbitStateEnumQuery.init_enums("sat:orbit_state", query_block, [x.value for x in SATOrbitStateEnum])
        self.orbit_state_vectors = _NullCheck("sat:orbit_state_vectors", query_block)
        self.platform_international_designator = _StringQuery("sat:platform_international_designator", query_block)
        self.relative_orbit = _NumberQuery.init_with_limits("sat:relative_orbit", query_block, min_value=1, max_value=None, is_int=True)


class _ViewExtension(_Extension):
    """
    STAC View Geometry Extension for STAC Items and STAC Collections.

    ...

    Attributes
    ----------
    azimuth: _NumberQuery
        number query interface for searching items by the view:azimuth field where the minimum value is 0 and the max value is 360. Float input.
    incidence_angle: _NumberQuery
        number query interface for searching items by the view:incidence_angle field where the minimum value is 0 and the max value is 90. Float input.
    off_nadir: _NumberQuery
        number query interface for searching items by the view:off_nadir field where the minimum value is 0 and the max value is 90. Float input.
    sun_azimuth: _NumberQuery
        number query interface for searching items by the view:sun_azimuth field where the minimum value is 0 and the max value is 360. Float input.
    sun_elevation: _NumberQuery
        number query interface for searching items by the view:sun_elevation field where the minimum value is -90 and the max value is 90. Float input.
    """
    def __init__(self, query_block: QueryBuilder):
        super().__init__(query_block)
        self.azimuth = _NumberQuery.init_with_limits("view:azimuth", query_block, min_value=0, max_value=360, is_int=False)
        self.incidence_angle = _NumberQuery.init_with_limits("view:incidence_angle", query_block, min_value=0, max_value=90, is_int=False)
        self.off_nadir = _NumberQuery.init_with_limits("view:off_nadir", query_block, min_value=0, max_value=90, is_int=False)
        self.sun_azimuth = _NumberQuery.init_with_limits("view:sun_azimuth", query_block, min_value=0, max_value=360, is_int=False)
        self.sun_elevation = _NumberQuery.init_with_limits("view:sun_elevation", query_block, min_value=-90, max_value=90, is_int=False)


class _UmbraExtension(_Extension):
    """
    STAC Extension for Umbra STAC Items .

    ...

    Attributes
    ----------
    best_resolution_azimuth_meters: _NumberQuery
        number query interface for searching items by the umbra:best_resolution_azimuth_meters field where the minimum value is 0. Float input.
    best_resolution_range_meters: _NumberQuery
        number query interface for searching items by the umbra:best_resolution_range_meters field where the minimum value is 0. Float input.
    collect_id : _StringQuery
        string query interface for searching items by the umbra:collect_id field
    collect_ids : _NullCheck
        field can be checked to see if umbra:collect_ids is null
    grazing_angle_degrees: _NumberQuery
        number query interface for searching items by the umbra:grazing_angle_degrees field. Float input.
    organization_id : _StringQuery
        string query interface for searching items by the umbra:organization_id field
    platform_pair : _StringQuery
        string query interface for searching items by the umbra:platform_pair field
    slant_range_meters: _NumberQuery
        number query interface for searching items by the umbra:slant_range_meters field. Float input.
    squint_angle_degrees_off_broadside: _NumberQuery
        number query interface for searching items by the umbra:squint_angle_degrees_off_broadside field where the minimum value is 0 and the max value is 90. Float input.
    squint_angle_engineering_degrees: _NumberQuery
        number query interface for searching items by the umbra:squint_angle_engineering_degrees field where the minimum value is -180 and the max value is 180. Float input.
    squint_angle_exploitation_degrees: _NumberQuery
        number query interface for searching items by the umbra:squint_angle_exploitation_degrees field where the minimum value is -90 and the max value is 90. Float input.
    target_azimuth_angle_degrees: _NumberQuery
        number query interface for searching items by the umbra:target_azimuth_angle_degrees field where the minimum value is 0 and the max value is 360. Float input.
    task_id : _StringQuery
        string query interface for searching items by the umbra:task_id field
    """
    def __init__(self, query_block: QueryBuilder):
        super().__init__(query_block)
        self.best_resolution_azimuth_meters = _NumberQuery.init_with_limits("umbra:best_resolution_azimuth_meters", query_block, min_value=0, max_value=None, is_int=False)
        self.best_resolution_range_meters = _NumberQuery.init_with_limits("umbra:best_resolution_range_meters", query_block, min_value=0, max_value=None, is_int=False)
        self.collect_id = _StringQuery("umbra:collect_id", query_block)
        self.collect_ids = _NullCheck("umbra:collect_ids", query_block)
        self.grazing_angle_degrees = _NumberQuery.init_with_limits("umbra:grazing_angle_degrees", query_block, min_value=None, max_value=None, is_int=False)
        self.organization_id = _StringQuery("umbra:organization_id", query_block)
        self.platform_pair = _StringQuery("umbra:platform_pair", query_block)
        self.slant_range_meters = _NumberQuery.init_with_limits("umbra:slant_range_meters", query_block, min_value=None, max_value=None, is_int=False)
        self.squint_angle_degrees_off_broadside = _NumberQuery.init_with_limits("umbra:squint_angle_degrees_off_broadside", query_block, min_value=0, max_value=90, is_int=False)
        self.squint_angle_engineering_degrees = _NumberQuery.init_with_limits("umbra:squint_angle_engineering_degrees", query_block, min_value=-180, max_value=180, is_int=False)
        self.squint_angle_exploitation_degrees = _NumberQuery.init_with_limits("umbra:squint_angle_exploitation_degrees", query_block, min_value=-90, max_value=90, is_int=False)
        self.target_azimuth_angle_degrees = _NumberQuery.init_with_limits("umbra:target_azimuth_angle_degrees", query_block, min_value=0, max_value=360, is_int=False)
        self.task_id = _StringQuery("umbra:task_id", query_block)


class QueryBuilder:
    """
    class for building cql2-json queries

    ...

    Attributes
    ----------
    id : _StringQuery
        string query interface for identifier is unique within a Collection
    collection : _StringQuery
        string query interface for limiting query by collection(s)
    datetime : _DateQuery
        datetime query interface for searching the datetime of assets
    geometry : _SpatialQuery
        spatial query interface
    created : _DateQuery
        datetime query interface for searching items by the created field
    updated : _DateQuery
        datetime query interface for searching items by the updated field
    start_datetime : _DateQuery
        datetime query interface for searching items by the start_datetime field
    end_datetime : _DateQuery
        datetime query interface for searching items by the end_datetime field
    platform : _StringQuery
        string query interface for searching items by the platform field
    constellation : _StringQuery
        string query interface for searching items by the constellation field
    mission : _StringQuery
        string query interface for searching items by the mission field
    gsd: _NumberQuery
        number query interface for searching items by the gsd field
    """
    _sort_by_field = None
    _sort_by_direction = "asc"

    def __init__(self):
        self._filter_expressions: list[_QueryTuple] = []
        self.id = _StringQuery("id", self)
        self.collection = _StringQuery("collection", self)
        self.datetime = _DateQuery("datetime", self)
        self.geometry = _SpatialQuery("geometry", self)
        self.created = _DateQuery("created", self)
        self.updated = _DateQuery("updated", self)
        self.start_datetime = _DateQuery("start_datetime", self)
        self.end_datetime = _DateQuery("end_datetime", self)
        self.platform = _StringQuery("platform", self)
        self.constellation = _StringQuery("constellation", self)
        self.mission = _StringQuery("mission", self)
        self.gsd = _NumberQuery.init_with_limits("gsd", self, min_value=0)
        self.pl = _PlExtension(self)
        self.eo = _EOExtension(self)
        self.landsat = _LandsatExtension(self)
        self.mlm = _MLMExtension(self)
        self.proj = _ProjExtension(self)
        self.sar = _SARExtension(self)
        self.sat = _SatExtension(self)
        self.view = _ViewExtension(self)
        self.umbra = _UmbraExtension(self)

    def query_dump(self, top_level_is_or=False, limit: Optional[int] = None):
        properties = list(vars(self).values())
        args = [x._build_query() for x in properties if isinstance(x, _QueryBase) and x._build_query() is not None]
        for query_filter in self._filter_expressions:
            args.append(query_filter._build_query())

        for p in properties:
            if isinstance(p, _Extension):
                args.extend(p._build_query())

        if len(args) == 0:
            return None
        top_level_op = "and"
        if top_level_is_or:
            top_level_op = "or"
        post_body = {
            "filter-lang": "cql2-json",
            "filter": {
                "op": top_level_op,
                "args": args}
        }
        if limit:
            post_body["limit"] = limit
        if self._sort_by_field:
            post_body["sortby"] = [{"field": self._sort_by_field, "direction": self._sort_by_direction}]
        return post_body

    def query_dump_json(self, top_level_is_or=False, indent=None, sort_keys=False, limit: Optional[int] = None):
        return json.dumps(self.query_dump(top_level_is_or=top_level_is_or, limit=limit),
                          indent=indent,
                          sort_keys=sort_keys,
                          cls=_DateTimeEncoder)

    def filter(self, *column_expression):
        query_tuple = column_expression[0]
        self._filter_expressions.append(query_tuple)


def filter_grouping(*column_expression):
    filter_tuple = _FilterTuple(column_expression[0].left, column_expression[0].op, column_expression[0].right)
    return filter_tuple

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
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


class StringQuery(QueryBase):
    _in_values = None
    _like_value = None
    _eq_value = None

    def equals(self, value) -> QueryBlock:
        self._check()
        self._eq_value = value
        return self._parent_obj

    def in_set(self, values: list[str]) -> QueryBlock:
        self._check()
        self._in_values = values
        return self._parent_obj

    def like(self, value: str) -> QueryBlock:
        self._check()
        self._like_value = value
        return self._parent_obj

    def _check(self):
        if self._in_values is not None or self._eq_value is not None or self._like_value is not None:
            raise ValueError("eq, in or like cannot already be set")

    def build_query(self):
        if self._eq_value is not None:
            return {
                "op": "=",
                "args": [self.property_obj, self._eq_value]
            }
        elif self._like_value is not None:
            return {
                "op": "like",
                "args": [
                    self.property_obj,
                    self._like_value
                ]
            }
        elif self._in_values is not None and len(self._in_values) > 0:
            return {
                "op": "in",
                "args": [
                    self.property_obj,
                    self._in_values
                ]
            }
        return None


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
        self._eq_value = value
        return self._parent_obj

    def gt(self, value) -> QueryBlock:
        self._greater_check(value)
        self._gt_value = value
        self._gt_operand = ">"
        return self._parent_obj

    def gte(self, value) -> QueryBlock:
        self._greater_check(value)
        self._gt_value = value
        self._gt_operand = ">="
        return self._parent_obj

    def lt(self, value) -> QueryBlock:
        self._less_check(value)
        self._lt_value = value
        self._lt_operand = "<"
        return self._parent_obj

    def lte(self, value) -> QueryBlock:
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

    def equals(self, value):
        # self._equals_check()
        self._eq_value = value
        return self._parent_obj

    @classmethod
    def init_with_limits(cls, field_name, parent_obj: QueryBlock, min_value=None, max_value=None):
        c = NumberQuery(field_name, parent_obj)
        c._min_value = min_value
        c._max_value = max_value
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


class QueryBlock:
    def __init__(self):
        self._filter_expressions: list[QueryTuple] = []

    def build_query(self, top_level_is_or=False):
        v = list(vars(self).values())
        args = [x.build_query() for x in v if isinstance(x, QueryBase) and x.build_query() is not None]
        for query_filter in self._filter_expressions:
            args.append(query_filter.build_query())
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

    def filter(self, *column_expresion):
        query_tuple = column_expresion[0]
        self._filter_expressions.append(query_tuple)


class STACQueryBlock(QueryBlock):
    def __init__(self):
        super(STACQueryBlock, self).__init__()
        self.datetime = DateQuery("datetime", self)
        self.updated = DateQuery("updated", self)
        self.created = DateQuery("created", self)
        self.id = StringQuery("id", self)
        self.platform = StringQuery("platform", self)
        self.geometry = SpatialQuery("geometry", self)
        self.gsd = NumberQuery.init_with_limits("gsd", self, min_value=0)


def filter_grouping(*column_expression):
    filter_tuple = FilterTuple(column_expression[0].left, column_expression[0].op, column_expression[0].right)
    return filter_tuple

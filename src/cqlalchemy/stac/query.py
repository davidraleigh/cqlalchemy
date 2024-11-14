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


class Accelerator(Enum):
    amd64 = "amd64"
    cuda = "cuda"
    xla = "xla"
    amd_rocm = "amd-rocm"
    intel_ipex_cpu = "intel-ipex-cpu"
    intel_ipex_gpu = "intel-ipex-gpu"
    macos_arm = "macos-arm"


class AcceleratorQuery(EnumQuery):
    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBlock, enum_fields: list[str]):
        o = AcceleratorQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: Accelerator) -> QueryBlock:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def in_set(self, values: list[Accelerator]) -> QueryBlock:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj

    def amd64(self) -> QueryBlock:
        return self.equals(Accelerator.amd64)

    def cuda(self) -> QueryBlock:
        return self.equals(Accelerator.cuda)

    def xla(self) -> QueryBlock:
        return self.equals(Accelerator.xla)

    def amd_rocm(self) -> QueryBlock:
        return self.equals(Accelerator.amd_rocm)

    def intel_ipex_cpu(self) -> QueryBlock:
        return self.equals(Accelerator.intel_ipex_cpu)

    def intel_ipex_gpu(self) -> QueryBlock:
        return self.equals(Accelerator.intel_ipex_gpu)

    def macos_arm(self) -> QueryBlock:
        return self.equals(Accelerator.macos_arm)


class Framework(Enum):
    PyTorch = "PyTorch"
    TensorFlow = "TensorFlow"
    scikit_learn = "scikit-learn"
    Hugging_Face = "Hugging Face"
    Keras = "Keras"
    ONNX = "ONNX"
    rgee = "rgee"
    spatialRF = "spatialRF"
    JAX = "JAX"
    MXNet = "MXNet"
    Caffe = "Caffe"
    PyMC = "PyMC"
    Weka = "Weka"


class FrameworkQuery(EnumQuery):
    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBlock, enum_fields: list[str]):
        o = FrameworkQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: Framework) -> QueryBlock:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def in_set(self, values: list[Framework]) -> QueryBlock:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj

    def PyTorch(self) -> QueryBlock:
        return self.equals(Framework.PyTorch)

    def TensorFlow(self) -> QueryBlock:
        return self.equals(Framework.TensorFlow)

    def scikit_learn(self) -> QueryBlock:
        return self.equals(Framework.scikit_learn)

    def Hugging_Face(self) -> QueryBlock:
        return self.equals(Framework.Hugging_Face)

    def Keras(self) -> QueryBlock:
        return self.equals(Framework.Keras)

    def ONNX(self) -> QueryBlock:
        return self.equals(Framework.ONNX)

    def rgee(self) -> QueryBlock:
        return self.equals(Framework.rgee)

    def spatialRF(self) -> QueryBlock:
        return self.equals(Framework.spatialRF)

    def JAX(self) -> QueryBlock:
        return self.equals(Framework.JAX)

    def MXNet(self) -> QueryBlock:
        return self.equals(Framework.MXNet)

    def Caffe(self) -> QueryBlock:
        return self.equals(Framework.Caffe)

    def PyMC(self) -> QueryBlock:
        return self.equals(Framework.PyMC)

    def Weka(self) -> QueryBlock:
        return self.equals(Framework.Weka)


class MLMExtension(Extension):
    """
    This object represents the metadata for a Machine Learning Model (MLM) used in STAC documents.
    """
    def __init__(self, query_block: QueryBlock):
        super().__init__(query_block)
        self.accelerator = AcceleratorQuery.init_enums("mlm:accelerator", query_block, [x.value for x in Accelerator])
        self.accelerator_constrained = BooleanQuery("field_name", query_block)
        self.accelerator_count = NumberQuery.init_with_limits("mlm:accelerator_count", query_block, min_value=1, max_value=None, is_int=True)
        self.accelerator_summary = StringQuery("mlm:accelerator_summary", query_block)
        self.architecture = StringQuery("mlm:architecture", query_block)
        self.batch_size_suggestion = NumberQuery.init_with_limits("mlm:batch_size_suggestion", query_block, min_value=0, max_value=None, is_int=True)
        self.framework = FrameworkQuery.init_enums("mlm:framework", query_block, [x.value for x in Framework])
        self.framework_version = StringQuery("mlm:framework_version", query_block)
        self.memory_size = NumberQuery.init_with_limits("mlm:memory_size", query_block, min_value=0, max_value=None, is_int=True)
        self.name = StringQuery("mlm:name", query_block)
        self.pretrained = BooleanQuery("field_name", query_block)
        self.pretrained_source = StringQuery("mlm:pretrained_source", query_block)
        self.total_parameters = NumberQuery.init_with_limits("mlm:total_parameters", query_block, min_value=0, max_value=None, is_int=True)


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

    def P(self) -> QueryBlock:
        return self.equals(FrequencyBand.P)

    def L(self) -> QueryBlock:
        return self.equals(FrequencyBand.L)

    def S(self) -> QueryBlock:
        return self.equals(FrequencyBand.S)

    def C(self) -> QueryBlock:
        return self.equals(FrequencyBand.C)

    def X(self) -> QueryBlock:
        return self.equals(FrequencyBand.X)

    def Ku(self) -> QueryBlock:
        return self.equals(FrequencyBand.Ku)

    def K(self) -> QueryBlock:
        return self.equals(FrequencyBand.K)

    def Ka(self) -> QueryBlock:
        return self.equals(FrequencyBand.Ka)


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

    def left(self) -> QueryBlock:
        return self.equals(ObservationDirection.left)

    def right(self) -> QueryBlock:
        return self.equals(ObservationDirection.right)


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

    def ascending(self) -> QueryBlock:
        return self.equals(OrbitState.ascending)

    def descending(self) -> QueryBlock:
        return self.equals(OrbitState.descending)

    def geostationary(self) -> QueryBlock:
        return self.equals(OrbitState.geostationary)


class SatExtension(Extension):
    """
    STAC Sat Extension to a STAC Item.
    """
    def __init__(self, query_block: QueryBlock):
        super().__init__(query_block)
        self.absolute_orbit = NumberQuery.init_with_limits("sat:absolute_orbit", query_block, min_value=1, max_value=None, is_int=True)
        self.anx_datetime = DateQuery("field_name", query_block)
        self.orbit_cycle = NumberQuery.init_with_limits("sat:orbit_cycle", query_block, min_value=1, max_value=None, is_int=True)
        self.orbit_state = OrbitStateQuery.init_enums("sat:orbit_state", query_block, [x.value for x in OrbitState])
        self.platform_international_designator = StringQuery("sat:platform_international_designator", query_block)
        self.relative_orbit = NumberQuery.init_with_limits("sat:relative_orbit", query_block, min_value=1, max_value=None, is_int=True)


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


class ProjExtension(Extension):
    """
    STAC Projection Extension for STAC Items.
    """
    def __init__(self, query_block: QueryBlock):
        super().__init__(query_block)
        self.code = StringQuery("proj:code", query_block)
        self.geometry = SpatialQuery("proj:geometry", query_block)
        self.wkt2 = StringQuery("proj:wkt2", query_block)


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

    def pan(self) -> QueryBlock:
        return self.equals(CommonName.pan)

    def coastal(self) -> QueryBlock:
        return self.equals(CommonName.coastal)

    def blue(self) -> QueryBlock:
        return self.equals(CommonName.blue)

    def green(self) -> QueryBlock:
        return self.equals(CommonName.green)

    def green05(self) -> QueryBlock:
        return self.equals(CommonName.green05)

    def yellow(self) -> QueryBlock:
        return self.equals(CommonName.yellow)

    def red(self) -> QueryBlock:
        return self.equals(CommonName.red)

    def rededge(self) -> QueryBlock:
        return self.equals(CommonName.rededge)

    def rededge071(self) -> QueryBlock:
        return self.equals(CommonName.rededge071)

    def rededge075(self) -> QueryBlock:
        return self.equals(CommonName.rededge075)

    def rededge078(self) -> QueryBlock:
        return self.equals(CommonName.rededge078)

    def nir(self) -> QueryBlock:
        return self.equals(CommonName.nir)

    def nir08(self) -> QueryBlock:
        return self.equals(CommonName.nir08)

    def nir09(self) -> QueryBlock:
        return self.equals(CommonName.nir09)

    def cirrus(self) -> QueryBlock:
        return self.equals(CommonName.cirrus)

    def swir16(self) -> QueryBlock:
        return self.equals(CommonName.swir16)

    def swir22(self) -> QueryBlock:
        return self.equals(CommonName.swir22)

    def lwir(self) -> QueryBlock:
        return self.equals(CommonName.lwir)

    def lwir11(self) -> QueryBlock:
        return self.equals(CommonName.lwir11)

    def lwir12(self) -> QueryBlock:
        return self.equals(CommonName.lwir12)


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


class CollectionCategory(Enum):
    A1 = "A1"
    A2 = "A2"
    T1 = "T1"
    T2 = "T2"
    RT = "RT"


class CollectionCategoryQuery(EnumQuery):
    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBlock, enum_fields: list[str]):
        o = CollectionCategoryQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: CollectionCategory) -> QueryBlock:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def in_set(self, values: list[CollectionCategory]) -> QueryBlock:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj

    def A1(self) -> QueryBlock:
        return self.equals(CollectionCategory.A1)

    def A2(self) -> QueryBlock:
        return self.equals(CollectionCategory.A2)

    def T1(self) -> QueryBlock:
        return self.equals(CollectionCategory.T1)

    def T2(self) -> QueryBlock:
        return self.equals(CollectionCategory.T2)

    def RT(self) -> QueryBlock:
        return self.equals(CollectionCategory.RT)


class Correction(Enum):
    L1TP = "L1TP"
    L1GT = "L1GT"
    L1GS = "L1GS"
    L2SR = "L2SR"
    L2SP = "L2SP"


class CorrectionQuery(EnumQuery):
    @classmethod
    def init_enums(cls, field_name, parent_obj: QueryBlock, enum_fields: list[str]):
        o = CorrectionQuery(field_name, parent_obj)
        o._enum_values = set(enum_fields)
        return o

    def equals(self, value: Correction) -> QueryBlock:
        self._check([value.value])
        self._eq_value = value.value
        return self._parent_obj

    def in_set(self, values: list[Correction]) -> QueryBlock:
        extracted = [x.value for x in values]
        self._check(extracted)
        self._in_values = extracted
        return self._parent_obj

    def L1TP(self) -> QueryBlock:
        return self.equals(Correction.L1TP)

    def L1GT(self) -> QueryBlock:
        return self.equals(Correction.L1GT)

    def L1GS(self) -> QueryBlock:
        return self.equals(Correction.L1GS)

    def L2SR(self) -> QueryBlock:
        return self.equals(Correction.L2SR)

    def L2SP(self) -> QueryBlock:
        return self.equals(Correction.L2SP)


class LandsatExtension(Extension):
    """
    Landsat Extension to STAC Items.
    """
    def __init__(self, query_block: QueryBlock):
        super().__init__(query_block)
        self.cloud_cover_land = NumberQuery.init_with_limits("landsat:cloud_cover_land", query_block, min_value=-1, max_value=100)
        self.collection_category = CollectionCategoryQuery.init_enums("landsat:collection_category", query_block, [x.value for x in CollectionCategory])
        self.collection_number = StringQuery("landsat:collection_number", query_block)
        self.correction = CorrectionQuery.init_enums("landsat:correction", query_block, [x.value for x in Correction])
        self.product_generated = DateQuery("field_name", query_block)
        self.scene_id = StringQuery("landsat:scene_id", query_block)
        self.wrs_path = StringQuery("landsat:wrs_path", query_block)
        self.wrs_row = StringQuery("landsat:wrs_row", query_block)
        self.wrs_type = StringQuery("landsat:wrs_type", query_block)


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
        self.mlm = MLMExtension(self)
        self.sar = SARExtension(self)
        self.sat = SatExtension(self)
        self.view = ViewExtension(self)
        self.proj = ProjExtension(self)
        self.eo = EOExtension(self)
        self.landsat = LandsatExtension(self)

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

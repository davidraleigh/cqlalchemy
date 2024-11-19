import json
from datetime import date, datetime, timedelta

from shapely import Point

from cqlalchemy.stac import query as q
from cqlalchemy.stac.query import QueryBuilder, _DateTimeEncoder, filter_grouping

if __name__ == '__main__':
    import uuid
    query = q.QueryBuilder().datetime.equals(date.today()).\
        updated.lt(datetime.now()).\
        created.delta(date.today(), timedelta(45))
    query.sar.resolution_azimuth.lte(45)
    query.id.equals(str(uuid.uuid4()))
    query.geometry.intersects(Point(4, 5))
    query.filter(((query.sar.resolution_azimuth == 45.1) | (query.datetime == 55.1) | (query.id == "stuff.1")) |
                 ((query.created >= datetime.now()) | (query.created <= datetime.now())))
    query.filter(filter_grouping((query.sar.resolution_azimuth >= 90.2) | (query.id == "pancakes.2")) &
                 (query.sar.resolution_azimuth == 45.2) & (query.datetime == 55.2) & (query.id == "stuff.2") &
                 (query.created >= datetime.now()) & (query.created <= datetime.now()))
    query.filter((query.sar.resolution_azimuth == 45.3) & (query.datetime == 55.3) & (query.id == "stuff.3") &
                 (query.created >= datetime.now()) & (query.created <= datetime.now()) &
                 filter_grouping((query.sar.resolution_azimuth >= 90.3) | (query.id == "pancakes.3")))
    print(json.dumps(query.query_dump(), indent=4, cls=_DateTimeEncoder))

    print(QueryBuilder().sar.resolution_azimuth.gt(99).sar.resolution_azimuth.lt(1).query_dump())
    print(QueryBuilder().filter(query.sar.resolution_azimuth > 100))

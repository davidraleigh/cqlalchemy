import json
from datetime import date, datetime, timedelta

from shapely import Point

from cqlalchemy.stac import query as q
from cqlalchemy.stac.query import DateTimeEncoder, QueryBlock, filter_grouping

if __name__ == '__main__':
    import uuid
    query = q.QueryBlock().datetime.equals(date.today()).\
        updated.lt(datetime.now()).\
        created.delta(date.today(), timedelta(45))
    query.cloud_cover.lte(45)
    query.id.equals(str(uuid.uuid4()))
    query.geometry.intersects(Point(4, 5))
    query.filter(((query.cloud_cover == 45.1) | (query.datetime == 55.1) | (query.id == "stuff.1")) |
                 ((query.created >= datetime.now()) | (query.created <= datetime.now())))
    query.filter(filter_grouping((query.cloud_cover >= 90.2) | (query.id == "pancakes.2")) &
                 (query.cloud_cover == 45.2) & (query.datetime == 55.2) & (query.id == "stuff.2") &
                 (query.created >= datetime.now()) & (query.created <= datetime.now()))
    query.filter((query.cloud_cover == 45.3) & (query.datetime == 55.3) & (query.id == "stuff.3") &
                 (query.created >= datetime.now()) & (query.created <= datetime.now()) &
                 filter_grouping((query.cloud_cover >= 90.3) | (query.id == "pancakes.3")))
    print(json.dumps(query.build_query(), indent=4, cls=DateTimeEncoder))

    print(QueryBlock().cloud_cover.gt(99).cloud_cover.lt(1).build_query())
    print(QueryBlock().filter(query.cloud_cover > 100))

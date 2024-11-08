import json
from datetime import date, datetime, timedelta

from shapely import Point

from cqlalchemy.stac import query as q
from cqlalchemy.stac.query import DateTimeEncoder, STACQueryBlock, filter_grouping

if __name__ == '__main__':
    import uuid
    query = q.STACQueryBlock().datetime.equals(date.today()).\
        updated.lt(datetime.now()).\
        created.delta(date.today(), timedelta(45))
    query.cloud_cover.lte(45)
    query.id.equals(str(uuid.uuid4()))
    query.geometry.intersects(Point(4, 5))
    query.filter(((query.cloud_cover == 45) | (query.datetime == 55) | (query.id == "stuff")) |
                 ((query.created >= datetime.now()) | (query.created <= datetime.now())))
    query.filter(filter_grouping((query.cloud_cover >= 90) | (query.id == "pancakes")) &
                 (query.cloud_cover == 45) & (query.datetime == 55) & (query.id == "stuff") &
                 (query.created >= datetime.now()) & (query.created <= datetime.now()))
    query.filter((query.cloud_cover == 45) & (query.datetime == 55) & (query.id == "stuff") &
                 (query.created >= datetime.now()) & (query.created <= datetime.now()) &
                 filter_grouping((query.cloud_cover >= 90) | (query.id == "pancakes")))
    print(json.dumps(query.build_query(), indent=4, cls=DateTimeEncoder))

    print(STACQueryBlock().cloud_cover.gt(99).cloud_cover.lt(1).build_query())
    print(STACQueryBlock().filter(query.cloud_cover > 100))

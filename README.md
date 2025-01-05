<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/<USER>/cqlalchemy.svg?branch=main)](https://cirrus-ci.com/github/<USER>/cqlalchemy)
[![ReadTheDocs](https://readthedocs.org/projects/cqlalchemy/badge/?version=latest)](https://cqlalchemy.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/cqlalchemy/main.svg)](https://coveralls.io/r/<USER>/cqlalchemy)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/cqlalchemy.svg)](https://anaconda.org/conda-forge/cqlalchemy)
[![Monthly Downloads](https://pepy.tech/badge/cqlalchemy/month)](https://pepy.tech/project/cqlalchemy)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/cqlalchemy)
-->

[![PyPI-Server](https://img.shields.io/pypi/v/cqlalchemy.svg)](https://pypi.org/project/cqlalchemy/)

# cqlalchemy

> Library to help make CQL2-json queries a little easier!

STAC is a terrific specification for cataloging temporal/spatial data with an emphasis on providing queryable fields for searching that data. One of the ways to make complex queries is to use [cql2-json](https://docs.ogc.org/DRAFTS/21-065.html).

This project provides two different functionalities. One is the `cqlalchemy.stac.query` module which provides query construction class (`QueryBuilder`) with the most popular extensions (eo, sar, sat, view, mlm).

The other functionality is a script that allows the user to build their own `QueryBuilder` class from extensions of their choosing, and allowing the opportunity to restrict the fields that can be queried (in the case where it isn't a required field and it's existence in the class might mislead the user).

## cqlalchemy QueryBuilder

### query by spatial extent
Either a geojson dict or a shapely geometry can be passed

<details><summary>Expand Python Code Sample</summary>

```python
import requests
from shapely.geometry import shape
from shapely.validation import make_valid
from cqlalchemy.stac.query import QueryBuilder

planetary_search = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
# request the geojson footprint of King County, Washington
url = "http://raw.githubusercontent.com/johan/world.geo.json/master/countries/USA/WA/King.geo.json"
r = requests.get(url)
geom_dict = r.json()['features'][0]['geometry']
geom = shape(geom_dict)
# fix missing vertices
geom = make_valid(geom)
q = QueryBuilder()
# planetary computer requires defining the constellation
q.collection.equals("landsat-c2-l2")
# define the spatial intersection
q.geometry.intersects(geom)
response = requests.post(planetary_search, q.query_dump_json(limit=2))
for feature in response.json()["features"]:
    print(feature["properties"]["datetime"])
    print(feature["properties"]["eo:cloud_cover"])
    print(feature["geometry"])
```

</details>

### query by date
querying using a python `date` object will query the 24 hour period of that day

<details><summary>Expand Python Code Sample</summary>

```python
import requests
from datetime import date
from cqlalchemy.stac.query import QueryBuilder

q = QueryBuilder()
# planetary computer requires defining the constellation
q.collection.equals("landsat-c2-l2")
# search entire utc 24 hour period for December 1st, 2023
q.datetime.equals(date(2023, 12, 1))
planetary_search = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
response = requests.post(planetary_search, q.query_dump_json(limit=2))
for feature in response.json()["features"]:
    print(feature["properties"]["datetime"])
```
</details>

results in
```shell
2023-12-01T23:59:27.570403Z
2023-12-01T23:59:03.607352Z
```
### query using an extension
We'll utilize the above query and request data from that date that's less than 30 percent cloud cover by using the Electro-Optical cloud cover field

<details><summary>Expand Python Code Sample</summary>

```python
import requests
from datetime import date
from cqlalchemy.stac.query import QueryBuilder

q = QueryBuilder()
# planetary computer requires defining the constellation
q.collection.equals("landsat-c2-l2")
# search entire utc 24 hour period for December 1st, 2023
q.datetime.equals(date(2023, 12, 1))
# either use the lt or lte methods
q.eo.cloud_cover.lt(30)

planetary_search = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
response = requests.post(planetary_search, q.query_dump_json(limit=2))
for feature in response.json()["features"]:
    print(feature["properties"]["datetime"])
    print(feature["properties"]["eo:cloud_cover"])
```
</details>

```shell
2023-12-01T23:56:15.912583Z
21.82
2023-12-01T23:54:16.177807Z
28.06
```

We continue to expand on the above extension utilizing the Landsat extension `cloud_cover_land` field.

<details><summary>Expand Python Code Sample</summary>

```python
import requests
from datetime import date
from cqlalchemy.stac.query import QueryBuilder

q = QueryBuilder()
# planetary computer requires defining the constellation
q.collection.equals("landsat-c2-l2")
# search entire utc 24 hour period for December 1st, 2023
q.datetime.equals(date(2023, 12, 1))
# either use the lt or lte methods
q.eo.cloud_cover.lt(30)

q.landsat.cloud_cover_land.lt(20)

planetary_search = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
response = requests.post(planetary_search, q.query_dump_json(limit=2))
for feature in response.json()["features"]:
    print(feature["properties"]["datetime"])
    print(feature["properties"]["eo:cloud_cover"])
    print(feature["properties"]["landsat:cloud_cover_land"])
```
</details>

The results reveal that some data may not have the cloud_cover_land field defined (this might be that they're not coastal data).
```shell
2023-12-01T23:52:40.414555Z
8.28
-1.0
2023-12-01T23:52:16.472683Z
5.39
-1.0
```

We can try again by forcing our search to be gt -1 and lt 20:

<details><summary>Expand Python Code Sample</summary>

```python
import requests
from datetime import date
from cqlalchemy.stac.query import QueryBuilder

q = QueryBuilder()
# planetary computer requires defining the constellation
q.collection.equals("landsat-c2-l2")
# search entire utc 24 hour period for December 1st, 2023
q.datetime.equals(date(2023, 12, 1))
# either use the lt or lte methods
q.eo.cloud_cover.lt(30)

q.landsat.cloud_cover_land.lt(20)
q.landsat.cloud_cover_land.gt(-1)

planetary_search = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
response = requests.post(planetary_search, q.query_dump_json(limit=2))
for feature in response.json()["features"]:
    print(feature["properties"]["datetime"])
    print(feature["properties"]["eo:cloud_cover"])
    print(feature["properties"]["landsat:cloud_cover_land"])
    print(feature["properties"]["platform"])
```
</details>

Now we're getting low land and overall cloud cover values. But it's only landsat-7. We can keep restricting the query by using the `q.platform.equals` query.
```shell
2023-12-01T23:32:54.374649Z
2.0
2.0
landsat-7
2023-12-01T23:32:30.478026Z
0.0
0.0
landsat-7
```

## cqlbuild

The `cqlbuild` is an interactive cli that allows for creating your own STAC cql2 query class.


### Interactive cqlbuild

Add various STAC extensions to the builder. Leave blank to complete adding extensions and move to next step.

#### Add extension schema by extension name
In some cases the extension schema can be guessed from an extension name. In the below example we use the `view` extension name:
```shell
 % cqlbuild --interactive
Enter extensions, either the path to a local file, a url or the extension json-ld name (sar, sat, etc):
STAC extension, raw schema url, local json extension schema file, local list of extensions or urls : view
treating input view like extension json-ld code and querying https://raw.githubusercontent.com/stac-extensions/view/refs/heads/main/json-schema/schema.json
STAC extension, raw schema url, local json extension schema file, local list of extensions or urls :
```

#### Add extension schema with local schema file
```shell
 % cqlbuild --interactive
Enter extensions, either the path to a local file, a url or the extension json-ld name (sar, sat, etc):
STAC extension, raw schema url, local json extension schema file, local list of extensions or urls : ./tests/test_data/mlm.schema.json
STAC extension, raw schema url, local json extension schema file, local list of extensions or urls :
```

#### Add extension schema by raw schema endpoint
```shell
 % cqlbuild --interactive
Enter extensions, either the path to a local file, a url or the extension json-ld name (sar, sat, etc):
STAC extension, raw schema url, local json extension schema file, local list of extensions or urls : https://stac-extensions.github.io/projection/v2.0.0/schema.json
STAC extension, raw schema url, local json extension schema file, local list of extensions or urls :
```

### Omitting fields from the query class interface

Omit fields from the query class interface by adding a field to ignore or a file with a list of fields to ignore.

```shell
Enter stac fields to omit from api or a path with a list of fields to omit:
Field to ignore : eo:snow_cover
Field to ignore : created
Field to ignore :
```
To prevent fields from being queryable through the generated STAC query interface.

### cqlbuild from definition file

Below is an example of a definition file for defining what extensions to use and what fields to ignore:
```json
{
  "extensions": [
    "sat",
    "sar",
    "eo",
    "view",
    "landsat",
    "./tests/test_data/mlm.schema.json",
    "https://stac-extensions.github.io/projection/v2.0.0/schema.json"
  ],
  "stac_fields_to_ignore": [
    "view:sun_azimuth",
    "view:sun_elevation",
    "constellation"
  ]
}
```

It can be used in the cli as follows:
```shell
% cqlbuild --definition ./tests/test_data/sample_definition.json --output ./tests/test_data/fixed_up_class.py
```

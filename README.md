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

## cqlbuild

The `cqlbuild` is an interactive cli that allows for creating your own STAC cql2 query class.

### Adding extensions

Add various STAC extensions to the builder. Leave blank to move to next step. In the below example we add the view, projection and mlm stac extensions.

#### Add extension schema by extension name
In some cases the extension schema can be guessed from an extension name
```shell
 % cqlbuild
Enter extensions, either the path to a local file, a url or the extension json-ld name (sar, sat, etc):
STAC extension, raw schema url, local json extension schema file, local list of extensions or urls : view
treating input view like extension json-ld code and querying https://raw.githubusercontent.com/stac-extensions/view/refs/heads/main/json-schema/schema.json
STAC extension, raw schema url, local json extension schema file, local list of extensions or urls :
```

#### Add extension schema with local schema file

```shell
 % cqlbuild
Enter extensions, either the path to a local file, a url or the extension json-ld name (sar, sat, etc):
STAC extension, raw schema url, local json extension schema file, local list of extensions or urls : ./tests/test_data/mlm.schema.json
STAC extension, raw schema url, local json extension schema file, local list of extensions or urls :
```

#### Add extension schema by raw schema endpoint
```shell
 % cqlbuild
Enter extensions, either the path to a local file, a url or the extension json-ld name (sar, sat, etc):
STAC extension, raw schema url, local json extension schema file, local list of extensions or urls : https://stac-extensions.github.io/projection/v2.0.0/schema.json
STAC extension, raw schema url, local json extension schema file, local list of extensions or urls :
```

#### Add extension by list of extension names and/or schema http endpoints
```shell
 % cqlbuild
Enter extensions, either the path to a local file, a url or the extension json-ld name (sar, sat, etc):
STAC extension, raw schema url, local json extension schema file, local list of extensions or urls : tests/test_data/sample_extension_list.txt
treating input sat like extension json-ld code and querying https://raw.githubusercontent.com/stac-extensions/sat/refs/heads/main/json-schema/schema.json
treating input sar like extension json-ld code and querying https://raw.githubusercontent.com/stac-extensions/sar/refs/heads/main/json-schema/schema.json
treating input eo like extension json-ld code and querying https://raw.githubusercontent.com/stac-extensions/eo/refs/heads/main/json-schema/schema.json
STAC extension, raw schema url, local json extension schema file, local list of extensions or urls :
```

### Omitting fields from the query class interface

Omit fields from the query class interface by adding a field to ignore or a file with a list of fields to ignore.

```shell
Enter stac fields to omit from api or a path with a list of fields to omit:
Field to ignore (or file of fields): eo:snow_cover
Field to ignore (or file of fields): created
Field to ignore (or file of fields): ./tests/test_data/ignore_fields.txt
Field to ignore (or file of fields):
```
To prevent fields from being queryable through the generated STAC query interface.
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

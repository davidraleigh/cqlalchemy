#!/bin/sh

cqlbuild --definition ./tests/test_data/query_1_definition.json --output ./tests/test_data/query_1.py
cqlbuild --definition ./tests/test_data/query_2_definition.json --output ./tests/test_data/query_2.py
cqlbuild --definition ./tests/test_data/query_definition.json --output ./src/cqlalchemy/stac/query.py
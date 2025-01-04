#!/bin/sh

poetry run pytest

if [ $? -eq 0 ]; then
  poetry publish --build
else
  echo "Pytest failed. fix failures before publishing"
fi

#!/bin/sh

# script/setup: Set up application for the first time after cloning, or set it
#               back to the initial first unused state.

set -e

if [ ! -d ".venv" ]; then
  python -m venv .venv
  echo "made venv at dir .venv"
fi

activate () {
    echo "activated .venv"
    . $PWD/.venv/bin/activate
}

activate

poetry install --all-extras -v

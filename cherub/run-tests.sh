#!/bin/bash

# need to execute everything from this directory
cd "$(dirname "$0")"

ERR_VENV=1

[ -d .venv ] || { echo "No virtual environment .venv found. Create it and install dependencies before running tests" >&2 ; exit $ERR_VENV ; }

if [ -d .venv/bin ]
then
    . .venv/bin/activate || exit $ERR_VENV
else
    . .venv/Scripts/activate || exit $ERR_VENV
fi

python -m unittest discover "$@"

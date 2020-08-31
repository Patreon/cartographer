#!/usr/bin/env bash

python3 -mvenv venv
./venv/bin/pip install -r dev-requirements.txt

cd example
python3 -mvenv venv
./venv/bin/pip install -r requirements.txt

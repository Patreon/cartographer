#!/usr/bin/env bash

python -mvenv venv
venv/bin/pip install -r dev-requirements.txt

cd example
python -mvenv venv
venv/bin/pip install -r requirements.txt

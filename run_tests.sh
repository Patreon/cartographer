#!/usr/bin/env bash
set -e

source venv/bin/activate >/dev/null
pip install -r requirements.txt >/dev/null
nosetests test/
deactivate

cd example
source venv/bin/activate >/dev/null
pip install -r requirements.txt >/dev/null
./run_tests.py
deactivate
cd ..
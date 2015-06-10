#!/bin/sh

pyvenv --system-site-packages venv
source venv/bin/activate
pip install flask
pip install sqlalchemy
git clone https://github.com/mitsuhiko/flask-sqlalchemy.git
cd flask-sqlalchemy
python3 setup.py install
cd ..
python3 server.py --debug --create-db

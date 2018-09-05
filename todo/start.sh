#!/bin/bash
export FLASK_APP=app.py
pip install -r requirements.txt
python tabledef.py
python app.py

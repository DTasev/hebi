#!/bin/bash

export PYTHONPATH=/webservice:$PYTHONPATH
export PYTHONUNBUFFERED=0
export FLASK_DEBUG=1
python -u -m webservice /hebi_config.json

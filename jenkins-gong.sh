#!/bin/bash

EXTENSION='1000@default'

python failed_jobs.py
if [ $? -eq 2 ]; then
    asterisk -rx "channel originate Local/$EXTENSION extension s@gong"
fi

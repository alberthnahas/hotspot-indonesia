#!/usr/bin/env bash

# Activate the virtual environment
if [ -f hs/bin/activate ]; then
    source hs/bin/activate
    echo "Activated virtual environment (hs)"
else
    echo "Virtual environment not found at hs/bin/activate"
fi

python3 hotspot_map.py

deactivate

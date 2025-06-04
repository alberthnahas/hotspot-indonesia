# Guidelines for agents working on this repository

This repository contains scripts that generate hotspot maps for Indonesia.

## Setup

1. **Python version**: Use Python 3.11 or newer.
2. **Virtual environment**: Create a virtual environment named `hs` in the repository root:
   ```bash
   python3 -m venv hs
   source hs/bin/activate
   ```
3. **Dependencies**: Install packages required by the scripts:
   ```bash
   pip install pandas geopandas matplotlib shapely
   ```

## Running

- To generate the hotspot map, execute:
  ```bash
  bash scripts/run_hotspot.sh
  ```
  The output image will be written to `images/update_hotspot.png`.

## Style and testing

- Format Python code with `black` before committing:
  ```bash
  black scripts/hotspot_map.py
  ```
- There is no automated test suite. Running `python3 scripts/hotspot_map.py` is recommended to verify the environment.

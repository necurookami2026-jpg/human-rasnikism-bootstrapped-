#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
export PYTHONDONTWRITEBYTECODE=1
command -v python3 >/dev/null
command -v node >/dev/null
python3 software/build_quilt.py
python3 software/build_program_library.py
python3 software/build_editions.py
python3 software/build_io_publication.py
python3 -m unittest discover -s software -v
for suite in software/test_*.cjs; do
    node "$suite"
done
python3 software/quilt.py --mode aantonymmakkakah --values 1 1

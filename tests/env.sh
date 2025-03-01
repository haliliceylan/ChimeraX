#!/usr/bin/env bash

# Run Pytest twice on this ONE file to test whether chimerax.core.__main__.init()
# runs the same whether it's called by running the ChimeraX binary or by
# running ChimeraX.app/bin/python -I -m chimerax.core

while getopts cs flag
do
  case "${flag}" in
    c) COVERAGE=true;;
    s) COV_SILENT=true;;
  esac
done

if [ "$COVERAGE" = true ]; then
  COVERAGE_ARGS="--cov=chimerax"
  if [ "$COV_SILENT" = true ]; then
    COVERAGE_ARGS="${COVERAGE_ARGS} --cov-report="
  fi
else
  COVERAGE_ARGS=""
fi

CHIMERAX_PYTHON_BIN=
CHIMERAX_BIN=

case $OSTYPE in
linux-gnu)
	CHIMERAX_PYTHON_BIN=./ChimeraX.app/bin/python3.11
	CHIMERAX_BIN=./ChimeraX.app/bin/ChimeraX
	;;
msys)
	CHIMERAX_PYTHON_BIN=./ChimeraX.app/bin/python.exe
	CHIMERAX_BIN=./ChimeraX.app/bin/ChimeraX-console.exe
	;;
darwin*)
	CHIMERAX_PYTHON_BIN=./ChimeraX.app/Contents/bin/python3.11
	CHIMERAX_BIN=./ChimeraX.app/Contents/bin/ChimeraX
	;;
esac

if [ ! -e "${CHIMERAX_PYTHON_BIN}" ]; then
	echo "No ChimeraX Python binary found" && exit 1
fi
if [ ! -e "${CHIMERAX_BIN}" ]; then
	echo "No ChimeraX binary found" && exit 1
fi

echo "Running Pytest on tests/test_env.py (ChimeraX)"
${CHIMERAX_BIN} -I -m pytest tests/test_env.py ${COVERAGE_ARGS}

echo "Running Pytest on tests/test_env.py (Python)"
${CHIMERAX_PYTHON_BIN} -I -m pytest tests/test_env.py ${COVERAGE_ARGS}

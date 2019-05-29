#!/usr/bin/env bash

set -e

export PATH=env/bin:${PATH}

echo "> Running tests..."
pytest --verbose --cov yuri/ --cov-report term --cov-report html tests/

echo "> Running benchmarks..."
pytest --verbose --benchmark-verbose benchmarks/

echo "> Running formatter..."
black yuri tests setup.py benchmarks --check

echo "> Running linter..."
flake8 yuri tests setup.py benchmarks --ignore=E128,E501

echo "> Running isort..."
isort -rc -c yuri tests setup.py benchmarks

echo "> Running type checker..."
mypy --strict-optional --ignore-missing-imports yuri tests benchmarks

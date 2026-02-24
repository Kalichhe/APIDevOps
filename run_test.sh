#!/bin/bash
docker compose up db_test -d
export ENV=test
fastapi dev app/main.py
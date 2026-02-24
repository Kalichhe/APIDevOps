#!/bin/bash
docker compose up db_dev -d
export ENV=development
fastapi dev app/main.py
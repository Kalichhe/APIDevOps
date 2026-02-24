#!/bin/bash
docker compose up db_prod -d
export ENV=production
fastapi run app/main.py
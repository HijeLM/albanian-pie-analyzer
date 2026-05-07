#!/bin/bash
echo "Seeding database..."
python3 scripts/seed_extended.py
echo "Starting server..."
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

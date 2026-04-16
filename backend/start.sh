#!/bin/bash
# Render deployment start script for AI DDR Generator API

echo "Starting AI DDR Generator API..."
uvicorn api:app --host 0.0.0.0 --port 10000 --workers 4

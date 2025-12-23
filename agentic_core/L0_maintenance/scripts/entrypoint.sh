#!/bin/bash
# Ensure logs directory exists and has correct permissions
mkdir -p /app/logs/thought_history
mkdir -p /app/logs/orchestrator
mkdir -p /app/logs/validation

# Execute the command passed to this script
exec "$@"

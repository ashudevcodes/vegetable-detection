#!/bin/bash

set -e

echo " Cleaning up object-detector project..."

echo " Stopping and removing containers..."
podman-compose down --volumes --remove-orphans || echo "⚠️ podman-compose failed or not installed"

echo " Removing project-specific images..."
podman images --format "{{.Repository}} {{.Id}}" | grep object-detector_ | awk '{print $2}' | xargs -r podman rmi -f

echo "✅ Cleanup complete."

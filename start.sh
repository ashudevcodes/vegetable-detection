#!/bin/bash

set -e

echo " Starting object-detector project with Podman..."

echo " Building services..."
podman-compose build

echo " Launching services..."
podman-compose up

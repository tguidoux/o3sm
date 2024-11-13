#! /usr/bin/env sh

# Exit in case of error
set -e

# version from first param
VERSION=$1

# exit if version is not set
if [ -z "$VERSION" ]; then
  echo "Version is not set"
  exit 1
fi

docker buildx build -t registry.guidoux.family/o3sm-frontend:$VERSION -t o3sm-frontend:$VERSION ./frontend -f ./frontend/Dockerfile --platform linux/arm64
docker buildx build -t registry.guidoux.family/o3sm-backend:$VERSION -t o3sm-backend:$VERSION ./backend -f ./backend/Dockerfile --platform linux/arm64

docker push registry.guidoux.family/o3sm-frontend:$VERSION
docker push registry.guidoux.family/o3sm-backend:$VERSION
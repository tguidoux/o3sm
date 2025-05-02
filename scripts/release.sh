#! /usr/bin/env sh

# Exit in case of error
set -e

# Ensure buildx builder exists and uses docker-container driver
if ! docker buildx inspect multiarch-builder >/dev/null 2>&1; then
  docker buildx create --name multiarch-builder --driver docker-container --use
else
  docker buildx use multiarch-builder
fi

# version from first param
VERSION=$1

# exit if version is not set
if [ -z "$VERSION" ]; then
  echo "Version is not set"
  exit 1
fi

docker buildx build --platform linux/arm64,linux/amd64 -t theoguidoux/o3sm-frontend:$VERSION -t o3sm-frontend:$VERSION ./frontend -f ./frontend/Dockerfile --push
docker buildx build --platform linux/arm64,linux/amd64 -t theoguidoux/o3sm-backend:$VERSION -t o3sm-backend:$VERSION ./backend -f ./backend/Dockerfile --push

docker manifest create theoguidoux/o3sm-frontend:$VERSION \
  --amend theoguidoux/o3sm-frontend:$VERSION
docker manifest create theoguidoux/o3sm-backend:$VERSION \
  --amend theoguidoux/o3sm-backend:$VERSION

docker manifest push theoguidoux/o3sm-frontend:$VERSION
docker manifest push theoguidoux/o3sm-backend:$VERSION
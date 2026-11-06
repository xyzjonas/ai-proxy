set dotenv-load := true

image := "scotch3840/ai-proxy:latest"

default:
  @just --list

# run locally (needs env vars, see README)
dev:
  uv run --with-requirements requirements.txt uvicorn main:app --reload

# build the production image
docker-build:
  docker build -t {{image}} .

# push the image to Docker Hub
docker: docker-build
  docker push {{image}}

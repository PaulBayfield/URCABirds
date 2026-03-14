FROM python:3.13-alpine
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apk add --no-cache git

COPY . ./URCABirdsAPI

WORKDIR /URCABirdsAPI

RUN uv sync

EXPOSE 7000

CMD ["uv", "run", "__main__.py"]

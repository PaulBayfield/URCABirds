# URCABirds API

URCABirds API is a RESTful API for the URCABirds project. It is built with Sanic and uses PostgreSQL for the database.

## Installation

```bash
uv sync
```

## Usage

```bash
uv run .\__main__.py
```

## Docker

```bash
docker build -t urcabirds-api .
docker run -p 7000:7000 urcabirds-api
```

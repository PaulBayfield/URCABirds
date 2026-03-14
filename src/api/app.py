from sanic import Sanic
from config import AppConfig
from components.middleware import Middleware
from components.ratelimit import Ratelimiter
from components.blueprint import BlueprintLoader
from components.errors import ErrorHandler
from utils.logger import Logger
from dotenv import load_dotenv
from os import environ
from textwrap import dedent
from asyncpg import create_pool
from aiohttp import ClientSession
from datetime import datetime
from pytz import timezone


load_dotenv(dotenv_path=".env")


# Application initialization
app = Sanic(
    name="URCABirdsAPI",
    config=AppConfig(),
)

# Adds information to the OpenAPI documentation
app.ext.openapi.raw(
    {
        "servers": [
            {
                "url": f"{environ.get('API_DOMAIN')}",
                "description": "Production server",
            }
        ],
    }
)

year = datetime.now(tz=timezone("Europe/Paris")).year

app.ext.openapi.add_security_scheme(
    "token",
    "http",
    scheme="bearer",
    bearer_format="JWT",
)

app.ext.openapi.describe(
    title=app.name,
    version=f"v{app.config.API_VERSION}",
    description=dedent(
        f"""
            # 🐦 • URCABirds API
            URCABirds is an automated bird detection system using passive audio monitoring and BirdNET-Analyzer.
            Sensor nodes continuously record audio and submit detections to this API.
            ⁣  
            The URCABirds API provides access to all recorded detections and statistics:
            - **Detections** — individual bird detection events (species, confidence, timestamp, sensor).  
            - **Sensors** — monitoring nodes and their activity.  
            - **Species** — all observed bird species and their aggregated statistics.  
            ⁣  
            # 🔒 • Authentication
            The **`POST /v1/detections`** endpoint requires a valid API key sent via the `Authorization` header:
            ```
            Authorization: Bearer <API_KEY>
            ```
            All other endpoints are publicly accessible.  
            However, **requests are rate-limited**.  
            ⁣  
            # 📩 • Contact
            For any questions or issues, please get in touch via the GitHub repository: [https://github.com/PaulBayfield/URCABirds](https://github.com/PaulBayfield/URCABirds)  
            ⁣  
            **URCABirds © 2025 - {year} | All rights reserved.**  
        """
    ),
)

# Logger registration
app.ctx.logs = Logger("logs")

# Rate limiter registration
app.ctx.ratelimiter = Ratelimiter()

# Middleware registration
Middleware(app)

# Route registration
BlueprintLoader(app).register()

# Error registration
ErrorHandler(app)


@app.listener("before_server_start")
async def setup_app(app: Sanic):
    app.ctx.session = ClientSession()

    # Database loading
    try:
        app.ctx.pool = await create_pool(
            database=environ["POSTGRES_DATABASE"],
            user=environ["POSTGRES_USER"],
            password=environ["POSTGRES_PASSWORD"],
            host=environ["POSTGRES_HOST"],
            port=environ["POSTGRES_PORT"],
            min_size=10,  # 10 connections
            max_size=10,  # 10 connections
            max_queries=50000,  # 50,000 queries
            loop=app.loop,
        )
    except OSError:
        app.ctx.logs.error("Failed to connect to the database!")
        app.ctx.logs.debug("Stopping API!")
        exit(1)

    app.ctx.logs.info("API started")


@app.listener("after_server_stop")
async def close_app(app: Sanic):
    await app.ctx.pool.close()
    await app.ctx.session.close()

    app.ctx.logs.info("API stopped")

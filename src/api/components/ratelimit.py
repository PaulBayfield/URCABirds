import binascii
import functools
import time

from exceptions.ratelimit import RatelimitException
from exceptions.forbidden import ForbiddenException
from sanic.request import Request
from sanic.response import HTTPResponse
from asyncpg import Pool


class Bucket:
    """
    Class representing a rate limiting bucket
    """

    def __init__(self, ident: str, limit: int, secs: int) -> None:
        """
        Initialises a new rate limiting bucket

        :param ident: Bucket identifier
        :type ident: str
        :param limit: Number of allowed requests
        :type limit: int
        :param secs: Bucket duration
        :type secs: int
        """
        self.ident = binascii.crc32(ident.encode())
        self.limit = limit
        self.secs = secs


class Ratelimiter:
    """
    Class to manage rate limits
    """

    DEFAULT = Bucket("default", 100, 60)

    def __init__(self) -> None:
        """
        Class initialization
        """
        self.ratelimits = {}
        self.last_ratelimit_cleanup = int(time.time())

        self.cache_buckets = {}
        self.cache_refresh = 300

    async def check_ratelimit(self, key: str, bucket: Bucket) -> dict:
        """
        Checks if a request is allowed

        :param key: Request key
        :type key: str
        :param bucket: Rate limiting bucket
        :type bucket: Bucket
        :return: Request headers
        :rtype: dict
        """
        await self.cleanup()

        current_time = int(time.time())
        self.ratelimits.setdefault(key, {})

        window_start = current_time // bucket.secs * bucket.secs

        self.ratelimits[key].setdefault(
            bucket.ident,
            {
                "remaining": bucket.limit,
                "reset": window_start + bucket.secs,
                "window_start": window_start,
            },
        )

        bucket_data = self.ratelimits[key][bucket.ident]

        if current_time >= bucket_data["reset"]:
            bucket_data["remaining"] = bucket.limit
            bucket_data["reset"] = window_start + bucket.secs
            bucket_data["window_start"] = window_start

        bucket_data["remaining"] -= 1

        headers = {
            "X-RateLimit-Limit": bucket.limit,
            "X-RateLimit-Remaining": max(bucket_data["remaining"], 0),
            "X-RateLimit-Reset": bucket_data["reset"]
            - current_time,  # Time remaining to reset
            "X-RateLimit-Bucket": bucket.ident,
            "X-RateLimit-Used": bucket.limit - bucket_data["remaining"],
        }

        if bucket_data["remaining"] < 0:
            headers.update({"Retry-After": bucket_data["reset"] - current_time})
            raise RatelimitException(
                headers=headers, extra={"cooldown": bucket_data["reset"] - current_time}
            )

        return headers

    async def cleanup(self) -> None:
        """
        Cleans up expired rate limits to free up memory
        """
        current_time = int(time.time())

        if current_time - self.last_ratelimit_cleanup < 60:
            return

        for key, buckets in self.ratelimits.items():
            for bucket, data in list(buckets.items()):
                if data["reset"] < current_time:
                    del self.ratelimits[key][bucket]

        self.last_ratelimit_cleanup = current_time

    async def getBucket(self, pool: Pool, key: str) -> Bucket:
        """
        Retrieves a bucket, either from cache or database if cache is expired or non-existent.
        Allows limiting database queries and having dynamic buckets.

        :param pool: Database connection pool
        :type pool: Pool
        :param key: Request key (IP or API Key)
        :type key: str
        :return: Bucket
        :rtype: Bucket
        """
        if key in self.cache_buckets and self.cache_buckets[key]["expires"] > int(
            time.time()
        ):
            if self.cache_buckets[key]["bucket"].limit == 0:
                raise ForbiddenException(
                    headers={
                        "X-RateLimit-Limit": 0,
                        "X-RateLimit-Remaining": 0,
                        "X-RateLimit-Reset": 0,
                        "X-RateLimit-Bucket": "banned",
                        "X-RateLimit-Used": 0,
                    },
                    extra={"ban": True},
                )
            else:
                return self.cache_buckets[key]["bucket"]
        else:
            self.cache_buckets[key] = {
                "expires": int(time.time()) + self.cache_refresh,
                "bucket": self.DEFAULT,
            }

            return self.DEFAULT


def ratelimit(default_bucket: Bucket = Ratelimiter.DEFAULT) -> callable:
    """
    Decorator to limit the number of requests per second

    :param default_bucket: Default bucket
    :type default_bucket: Bucket
    :return: Decorated function
    :rtype: callable
    """

    def wrapper(func: callable) -> callable:
        """
        Internal decorator function

        :param func: Function to decorate
        :type func: callable
        :return: Decorated function
        :rtype: callable
        """

        @functools.wraps(func)
        async def wrapped(request: Request, *args, **kwargs) -> HTTPResponse:
            """
            Internal decorator function

            :param request: Request
            :type request: Request
            :param args: Arguments
            :type args: tuple
            :param kwargs: Keyword arguments
            :type kwargs: dict
            :return: Response
            :rtype: HTTPResponse
            """
            key = request.headers.get("CF-Connecting-IP", request.client_ip)
            apikey = request.headers.get(
                "X-API-Key", None
            )  # For users with a dynamic IP address
            if apikey:
                key = apikey

            ratelimiter: Ratelimiter = request.app.ctx.ratelimiter

            pool: Pool = request.app.ctx.pool
            if pool:
                bucket: Bucket = await ratelimiter.getBucket(pool, key)

                # In some cases like CDN images, we want to apply the least restrictive limit
                if bucket.limit < default_bucket.limit:
                    bucket = default_bucket
            else:
                bucket = default_bucket

            headers = await ratelimiter.check_ratelimit(key, bucket)

            resp: HTTPResponse = await func(request, *args, **kwargs)
            resp.headers.update(headers)

            return resp

        return wrapped

    return wrapper

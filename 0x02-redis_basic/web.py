# web.py

import redis
import requests
from functools import wraps
from typing import Callable

def track_get_page(fn: Callable) -> Callable:
    """ Decorator for get_page function to cache and track URL access count
    """
    @wraps(fn)
    def wrapper(url: str) -> str:
        """ Wrapper that:
            - checks whether a URL's data is cached
            - tracks how many times the URL is accessed
        """
        # Connect to Redis server
        client = redis.Redis()

        # Check if URL data is cached
        cached_page = client.get(f'{url}')
        if cached_page:
            # URL data found in cache, return it
            client.incr(f'count:{url}')  # Increment access count
            return cached_page.decode('utf-8')

        # URL data not cached, make an HTTP request
        response = fn(url)

        # Cache the response with a 10-second expiration time
        client.setex(f'{url}', 10, response)

        # Increment access count
        client.incr(f'count:{url}')

        return response
    return wrapper

@track_get_page
def get_page(url: str) -> str:
    """ Makes an HTTP request to a given URL and returns the response text
    """
    response = requests.get(url)
    return response.text

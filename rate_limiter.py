"""
rate_limiter.py
A simple in-memory rate limiter.
Each user gets a max number of requests per minute.
If they go over, we block them with a 429 error (Too Many Requests).
"""

import time
from collections import defaultdict
from fastapi import HTTPException

# How many requests a user can make per window
MAX_REQUESTS = 5
WINDOW_SECONDS = 60

# Stores request timestamps per user
# Example: {"prashik": [1234567890.1, 1234567891.5, ...]}
user_requests = defaultdict(list)


def check_rate_limit(username: str):
    """
    Checks if a user has gone over their request limit.
    Raises HTTP 429 if they have. Otherwise records this new request.
    """
    now = time.time()

    # Keep only timestamps from within the last WINDOW_SECONDS
    user_requests[username] = [
        timestamp for timestamp in user_requests[username]
        if now - timestamp < WINDOW_SECONDS
    ]

    # If they already made MAX_REQUESTS in this window, block them
    if len(user_requests[username]) >= MAX_REQUESTS:
        oldest_request = user_requests[username][0]
        seconds_to_wait = round(WINDOW_SECONDS - (now - oldest_request))
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {seconds_to_wait} seconds."
        )

    # Record this request
    user_requests[username].append(now)


def get_remaining_requests(username: str) -> int:
    """Returns how many requests this user has left in the current window."""
    now = time.time()
    user_requests[username] = [
        timestamp for timestamp in user_requests[username]
        if now - timestamp < WINDOW_SECONDS
    ]
    return MAX_REQUESTS - len(user_requests[username])
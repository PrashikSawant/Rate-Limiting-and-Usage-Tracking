"""
backend.py
Day 20 - Rate Limiting + Usage Tracking

Flow:
1. User logs in -> gets a JWT token (from Day 18 auth.py)
2. User calls /chat with their token
3. Before answering, we check: has this user gone over their rate limit?
4. If allowed, we call Groq, log the usage to SQLite, and return the answer
5. User can check /usage to see their own stats
"""

import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from groq import Groq
from dotenv import load_dotenv

from auth import authenticate_user, create_access_token, verify_token
from rate_limiter import check_rate_limit, get_remaining_requests
from database import init_db, log_usage, get_usage_for_user

load_dotenv()

app = FastAPI(title="Day 20 - Rate Limiting + Usage Tracking")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Rough Groq LLaMA 3.3 70B pricing estimate (per 1M tokens) - adjust if pricing changes
COST_PER_1M_INPUT_TOKENS = 0.59
COST_PER_1M_OUTPUT_TOKENS = 0.79


@app.on_event("startup")
def startup():
    init_db()


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """Decodes the JWT token and returns the username, or raises 401."""
    try:
        return verify_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Takes username + password, returns a JWT token if correct."""
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = create_access_token(form_data.username)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/chat")
def chat(prompt: str, username: str = Depends(get_current_user)):
    """
    Main chat endpoint - protected by both JWT auth AND rate limiting.
    """
    # Step 1: Check rate limit BEFORE calling the expensive API
    check_rate_limit(username)

    # Step 2: Call Groq
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response.choices[0].message.content
    usage = response.usage

    # Step 3: Calculate estimated cost
    input_cost = (usage.prompt_tokens / 1_000_000) * COST_PER_1M_INPUT_TOKENS
    output_cost = (usage.completion_tokens / 1_000_000) * COST_PER_1M_OUTPUT_TOKENS
    estimated_cost = input_cost + output_cost

    # Step 4: Log this request to SQLite
    log_usage(
        username=username,
        endpoint="/chat",
        prompt_tokens=usage.prompt_tokens,
        completion_tokens=usage.completion_tokens,
        total_tokens=usage.total_tokens,
        estimated_cost=estimated_cost,
    )

    return {
        "answer": answer,
        "tokens_used": usage.total_tokens,
        "estimated_cost": round(estimated_cost, 6),
        "requests_remaining_this_minute": get_remaining_requests(username),
    }


@app.get("/usage")
def usage(username: str = Depends(get_current_user)):
    """Returns this user's full usage history and totals."""
    return get_usage_for_user(username)


@app.get("/")
def root():
    return {"message": "Day 20 API is running. Go to /docs to test it."}
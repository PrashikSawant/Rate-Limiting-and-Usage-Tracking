# ⏱️ Day 20 — Rate Limiting + Usage Tracking

Part of my **120-Day AI Engineering Bootcamp** (Day 20/120) — building one AI project a day to become job-ready.

## 🤔 Why I Built This

Every project so far assumed unlimited API calls. But real APIs cost money, and real users can accidentally (or intentionally) spam a system. Production AI apps need two things: a way to **stop abuse** (rate limiting) and a way to **see what's happening** (usage tracking). This project adds both on top of the JWT-authenticated API I built on Day 18-19.

## 🧠 Thought Process

1. Reuse the JWT auth from Day 18 — don't reinvent login
2. Add a rate limiter that tracks requests **per user**, not globally
3. Before calling the (paid) Groq API, check: has this user gone over their limit?
4. Log every successful request to a lightweight SQLite database — no extra server needed
5. Expose a `/usage` endpoint so users can see their own stats
6. Build a simple Streamlit UI to test login, chat, and usage in one place

## ⚙️ What It Does

- 🔐 Login with JWT (same as Day 18)
- 🚦 Rate limits each user to **5 requests per 60 seconds**
- 💬 `/chat` endpoint calls Groq's LLaMA 3.3 70B and returns the answer
- 💰 Calculates estimated cost per request based on token usage
- 📊 Logs every request (tokens, cost, timestamp) to SQLite
- 📈 `/usage` endpoint shows total requests, total tokens, and total cost per user

## 🛠️ Tech Stack

- **Python** — core logic
- **FastAPI** — backend API
- **Groq API (LLaMA 3.3 70B)** — the actual AI model
- **SQLite** — lightweight usage logging (no external DB needed)
- **python-jose** — JWT token creation/verification
- **passlib + bcrypt** — password hashing
- **Streamlit** — frontend UI for testing

## 🚀 How to Run

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd Day20-RateLimiting

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\activate      # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your keys to .env
# GROQ_API_KEY=your_key_here
# SECRET_KEY=your_random_secret_here

# 5. Run the backend (Terminal 1)
uvicorn backend:app --reload

# 6. Run the frontend (Terminal 2, new window)
streamlit run frontend.py
```

Login with username `prashik` / password `mypassword123`, then chat away — try sending 6+ messages quickly to see the rate limiter kick in.

## 💡 What I Learned

- Rate limiting isn't about being "mean" to users — it's about protecting the system (and the API bill) from abuse or runaway bugs
- A **sliding window** approach (tracking timestamps, not just a counter) handles edge cases better than a simple fixed counter
- SQLite is perfect for small-scale usage logging — no need for a heavy database for a project like this
- Streamlit reruns the **entire script** on every interaction — that's normal, not a bug, and important to understand when debugging "weird" behavior

## 🔮 What's Next

**Day 21 — Deploy Full Stack App** on Railway/Render, taking this rate-limited, tracked API live on the internet.

## 👤 About Me

I'm Prashik, building one AI project a day for 120 days to become a job-ready AI Engineer. Follow my journey on [LinkedIn](#) and [GitHub](#).

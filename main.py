from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

import apis

app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://nisarg851.github.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(apis.router)

def ping_self():
    try:
        response = requests.get("https://humberchatbotbackend.onrender.com")
        print(f"Self-ping successful! Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Self-ping failed: {e}")

if __name__ == "__main__":
    from apscheduler.schedulers.background import BackgroundScheduler
    from query_controllers import web_scrapper

    scheduler = BackgroundScheduler()
    scheduler.add_job(web_scrapper, "cron", day="1", hour=0, args=("http://careers.humber.ca",))
    scheduler.add_job(ping_self, 'interval', minutes=10)
    scheduler.start()

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
import random as rand
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import asyncio

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulated machine status
machines_status = {
    "Machine A": {"status": "running", "temperature": 75, "output_count": 1000},
    "Machine B": {"status": "idle", "temperature": 70, "output_count": 500},
    "Machine C": {"status": "error", "temperature": 80, "output_count": 0},
}

# A list to keep track of pending requests
pending_requests = []


# Route for long polling
@app.get("/long-polling")
async def long_polling(request: Request):
    while True:
        # Check for updates to the machine status
        updated_data = await check_for_updates()

        if updated_data:
            # If there are updates, return the data
            return JSONResponse(content=updated_data)

        # Wait for a short time before checking again
        await asyncio.sleep(1)


# Function to simulate checking for updates
async def check_for_updates():
    # Randomly simulate status updates for demonstration
    for machine in machines_status.keys():
        if rand.random() < 0.1:  # 10% chance to change the status
            machines_status[machine]["status"] = rand.choice(["running", "idle", "error"])
            machines_status[machine]["temperature"] = rand.randint(60, 90)
            machines_status[machine]["output_count"] = rand.randint(0, 1200)
            return {machine: machines_status[machine]}
    return None

# uvicorn main:app --reload --host 172.18.7.93 --port 8989

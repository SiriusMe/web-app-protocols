# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import random
from datetime import datetime
import asyncio
from typing import Dict, List
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulate machine data storage
machines_status: Dict[str, Dict] = {
    "machine_001": {
        "name": "CNC Milling Machine",
        "status": "running",
        "temperature": 45.5,
        "speed": 1200,
        "last_updated": datetime.now().isoformat()
    },
    "machine_002": {
        "name": "Robotic Arm",
        "status": "idle",
        "temperature": 35.2,
        "position": "home",
        "last_updated": datetime.now().isoformat()
    },
    "machine_003": {
        "name": "3D Printer",
        "status": "running",
        "temperature": 210.5,
        "progress": 45,
        "last_updated": datetime.now().isoformat()
    }
}


# Middleware to log requests and responses
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Generate request ID
    request_id = random.randint(1000, 9999)

    # Log the request
    logger.info(f"Request #{request_id}")
    logger.info(f"Method: {request.method}")
    logger.info(f"URL: {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")

    # Process the request
    response = await call_next(request)

    # Log the response
    logger.info(f"Response #{request_id}")
    logger.info(f"Status: {response.status_code}")

    return response


async def update_machine_data():
    while True:
        for machine_id in machines_status:
            if random.random() < 0.3:
                machines_status[machine_id]["status"] = random.choice([
                    "running", "idle", "maintenance", "error"
                ])

            current_temp = machines_status[machine_id]["temperature"]
            machines_status[machine_id]["temperature"] = round(
                current_temp + random.uniform(-0.5, 0.5), 1
            )

            machines_status[machine_id]["last_updated"] = datetime.now().isoformat()

        await asyncio.sleep(5)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_machine_data())


@app.get("/machines")
async def get_machines_status(request: Request):
    # Log the response data
    logger.info(f"Response data: {json.dumps(machines_status, indent=2)}")
    return machines_status


@app.get("/machine/{machine_id}")
async def get_machine_status(machine_id: str, request: Request):
    if machine_id in machines_status:
        # Log the response data
        logger.info(f"Response data for machine {machine_id}: {json.dumps(machines_status[machine_id], indent=2)}")
        return machines_status[machine_id]
    return {"error": "Machine not found"}
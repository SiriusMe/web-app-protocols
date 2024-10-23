import random as rand
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import logging
import json

app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

clients = []

# Serve static files from the "static" directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/sse")
async def sse(request: Request):
    response = StreamingResponse(
        sse_generator(request),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

# A generator function for sending SSE events
async def sse_generator(request: Request):
    client = Client()
    clients.append(client)
    logger.info(f"Client connected. Total clients: {len(clients)}")

    try:
        while True:
            # Generate structured random data
            data = {
                "value": rand.uniform(10, 200),
                "timestamp": asyncio.get_event_loop().time()
            }
            # Send the structured data as an SSE event
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(5)
    except asyncio.CancelledError:
        clients.remove(client)
        logger.info(f"Client disconnected. Total clients: {len(clients)}")

# A class to represent clients
class Client:
    def __init__(self):
        self.message_queue = asyncio.Queue()

@app.post("/send_message")
async def send_message(message: str):
    for client in clients:
        await client.message_queue.put(message)
    logger.info(f"Message sent to all clients: {message}")
    return {"message": "Message sent to all clients"}

# uvicorn main:app --reload --host localhost --port 8989

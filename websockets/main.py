from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect
import random
import asyncio

app = FastAPI()


# Simulate machine data generation (temperature, vibration, etc.)
async def machine_data_generator():
    while True:
        await asyncio.sleep(1)
        yield {
            "temperature": random.uniform(20, 100),  # temperature in °C
            "vibration": random.uniform(0, 10),  # vibration level
            "speed": random.uniform(1000, 3000)  # speed in RPM
        }


# Connection Manager to handle multiple clients (e.g., different machines)
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


# WebSocket endpoint to send real-time machine data
@app.websocket("/ws/machine-data")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        async for data in machine_data_generator():
            # Convert data to string and send to connected clients
            message = f"Temperature: {data['temperature']:.2f} °C, Vibration: {data['vibration']:.2f}, Speed: {data['speed']:.2f} RPM"

            # Check for alerts (example: if temperature > 80°C)
            if data["temperature"] > 80:
                alert_message = f"ALERT: Machine temperature too high: {data['temperature']:.2f} °C"
                await manager.broadcast(alert_message)
            else:
                await manager.broadcast(message)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

#uvicorn main:app --reload
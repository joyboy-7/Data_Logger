from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
import json

app = FastAPI()

# Store the dummy data and active WebSocket clients
dummy_data: List[List[float]] = []
active_clients: List[WebSocket] = []

# Template directory for HTML responses
templates = Jinja2Templates(directory=".")

@app.get("/")
async def get(request: Request):
    """
    Homepage showing real-time sensor data visualization
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_clients.append(websocket)
    try:
        while True:
            # Receive data from client (ESP32)
            data = await websocket.receive_text()
            print(f"Received data: {data}")
            
            # Parse and store the data
            try:
                columns = list(map(float, data.split(',')))
                if len(columns) == 16:
                    dummy_data.append(columns)
                    # Broadcast the new data to all connected clients
                    for client in active_clients:
                        await client.send_text(f"new_data:{','.join(map(str, columns))}")
                else:
                    print("Invalid data format, expecting 16 columns.")
            except ValueError as e:
                print(f"Error parsing data: {e}")

    except WebSocketDisconnect:
        active_clients.remove(websocket)
        print("Client disconnected")